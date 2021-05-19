import os
import re
import boto3
import shutil
from glob import glob

from django.conf import settings
from django.utils import timezone

from app.models import State, Location

if os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY'):
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    s3 = boto3.resource(
        's3', aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    s3_client = boto3.client(
        's3', aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    transcoder_client = boto3.client(
        'elastictranscoder', 'ap-northeast-1',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
else:
    s3 = boto3.resource('s3')
    s3_client = boto3.client('s3')
    transcoder_client = boto3.client('elastictranscoder', 'ap-northeast-1')


class Predict:
    def __init__(self, s3_bucket_name, s3_key):
        self.s3_bucket_name = s3_bucket_name
        self.s3_key = s3_key
        self.location_id = settings.LOCATION
        self.download_path = settings.DOWNLOAD_PATH
        self.images_path = settings.IMAGES_PATH
        self.save_path = settings.SAVE_PATH
        self.save_s3_bucket_name = settings.SAVE_S3_BUCKET_NAME
        self.thumbnail_sep_count = settings.THUMBNAIL_SEP_COUNT
        self.s3_folder = ''
        if '/' in self.s3_key:
            self.s3_folder, self.s3_key = self.s3_key.split('/')
        self.init_path()

    def init_path(self):
        # 保存先設定
        dir_name = '.'.join(self.s3_key.split('.')[:-1])
        self.download_path = os.path.join(self.download_path, dir_name)
        self.images_path = os.path.join(self.images_path, dir_name)
        self.save_path = os.path.join(self.save_path, dir_name)
        # 保存先なければ作成する
        for d in (self.download_path, self.images_path, self.save_path):
            if os.path.exists(d):
                continue
            os.makedirs(d)

    def detection(self):
        return True

    def run(self):
        if self.s3_folder.isdigit():
            self.location_id = int(self.s3_folder)
        location = Location.objects.get(pk=self.location_id)
        state = State(
            state_type=0,
            location=location,
        )
        state.save()
        # s3から動画ファイルを取得する
        url = '/'.join([self.s3_folder, self.s3_key]) if self.s3_folder else self.s3_key
        destfile = os.path.join(self.download_path, self.s3_key)
        s3_download(self.s3_bucket_name, url, destfile)
        # TODO: 動画を加工する処理を入れる
        s3_upload(self.save_s3_bucket_name, self.images_path, self.s3_key, is_public=True)
        # transcoderでhls作成
        hls_key = '.'.join(self.s3_key.split('.')[:-1])
        preset_id = create_transcoder_preset(hls_key)
        hls_url, thumb_url = create_transcoder_job(self.save_s3_bucket_name, self.s3_key, hls_key, preset_id=preset_id)
        delete_transcoder_preset(preset_id)
        # 推論結果と動画パスをStateに保存する
        save_state(state, 1, 1.0, hls_url, thumb_url, timezone.now())
        # 一時保存したファイルを削除
        for d in (self.download_path, self.images_path, self.save_path):
            shutil.rmtree(d)


def save_state(state, state_type, fps, movie_url, thumb_url, update_time):
    state.state_type = state_type
    state.fps = fps
    state.movie_url = movie_url
    state.thumb_url = thumb_url
    state.update_time = update_time
    state.save()


def images_to_movie(predict_results, save_dir, filename, fps):
    """画像ファイルを動画に変換する"""
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    # 保存先なければ作成する
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    filepath = os.path.join(save_dir, filename)
    fourcc = cv2.VideoWriter_fourcc(*settings.FOURCC)
    image_size = settings.IMAGE_SIZE
    video = cv2.VideoWriter(filepath, fourcc, fps, image_size)
    font = ImageFont.truetype(settings.FONT, settings.FONT_SIZE)
    for path, state, _ in predict_results:
        try:
            pil_img = Image.open(path)
        except OSError:
            continue
        pil_img = pil_img.resize(image_size)
        draw = ImageDraw.Draw(pil_img)
        text, fill = settings.NORMAL_TEXT if not state else settings.FAULT_TEXT
        draw.text(settings.TEXT_POS, text, fill=fill, font=font)
        draw.line((
            (0, 0), (image_size[0], 0),
            (image_size[0], 0), (image_size[0], image_size[1]),
            (image_size[0], image_size[1]), (0, image_size[1]),
            (0, image_size[1]), (0, 0)),
            fill=fill, width=settings.LINE_WIDTH,
        )
        img = np.asarray(pil_img)
        img = cv2.resize(img, image_size)
        video.write(img)
    video.release()
    return filepath


def movie_to_images(movie_file_path, save_path):
    """動画をフレーム単位の画像に変換する"""
    import cv2
    video = cv2.VideoCapture(movie_file_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    sec = 0.0
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    for i in range(count):
        _, frame = video.read()
        path = os.path.join(save_path, "%06d.jpg" % i)
        cv2.imwrite(path, frame)
        sec += 1 / fps
    return fps


def s3_download(bucket_name, url, destfile):
    bucket = s3.Bucket(bucket_name)
    bucket.download_file(url, destfile)


def s3_upload(bucket_name, save_filepath, s3_key, is_public=False):
    bucket = s3.Bucket(bucket_name)
    extra_args = {}
    if is_public:
        extra_args['ACL'] = 'public-read'
    bucket.upload_file(save_filepath, s3_key, ExtraArgs=extra_args)
    url = 'http://{}.s3.amazonaws.com/{}'.format(bucket_name, s3_key)
    return url


def s3_upload_obj(bucket_name, save_filename, file_obj):
    bucket = s3.Bucket(bucket_name)
    obj = bucket.Object(save_filename)
    obj.upload_fileobj(file_obj)


def is_exists(output_key, res_key, pat):
    """ファイルの存在確認
    """
    # m3u8ファイル
    if '{}.m3u8'.format(output_key) == res_key:
        return True
    # tsファイル or thumbnail
    elif re.match(pat, res_key):
        return True
    return False


def delete_exists_file(output_key, content_bucket, is_thumbnail=False):
    """S3上にファイルが存在する場合は削除する
    """
    if not is_thumbnail:
        pat = re.compile(r"%s[\d+]{5}.ts" % output_key)
    else:
        pat = re.compile(r"%s_[\d+]{5}.png" % output_key)

    res = s3_client.list_objects_v2(Prefix=output_key, Bucket=content_bucket)
    # 該当ファイルが存在しないときは処理なし
    if not res.get('Contents'):
        return
    for content in res['Contents']:
        if not is_exists(output_key, content['Key'], pat):
            continue
        s3_client.delete_object(Bucket=res['Name'], Key=content['Key'])


def create_transcoder_job(bucket_name, s3_key, hls_key, preset_id):
    pipeline_response = transcoder_client.list_pipelines(Ascending='true')
    pipeline_setting = [p for p in pipeline_response['Pipelines'] if p['InputBucket'] == bucket_name][0]
    pipeline_id = pipeline_setting['Id']
    content_bucket = pipeline_setting['ContentConfig']['Bucket']
    thumbnail_bucket = pipeline_setting['ThumbnailConfig']['Bucket']
    delete_exists_file(hls_key, content_bucket)
    delete_exists_file(hls_key, thumbnail_bucket, is_thumbnail=True)
    transcoder_client.create_job(
        PipelineId=pipeline_id,
        Input={
            'Key': s3_key,
            'FrameRate': 'auto',
            'Resolution': 'auto',
            'AspectRatio': 'auto',
            'Interlaced': 'auto',
            'Container': 'auto',
        },
        Output={
            'Key': hls_key,
            'ThumbnailPattern': hls_key + '_{count}',
            'PresetId': preset_id,
            'SegmentDuration': settings.SEGMENT_DURATION,
        },
    )
    movie_url = 'http://{}.s3.amazonaws.com/{}.m3u8'.format(content_bucket, hls_key)
    thumb_url = 'http://{}.s3.amazonaws.com/{}_00001.png'.format(thumbnail_bucket, hls_key)
    return movie_url, thumb_url



def create_transcoder_preset(key, interval=300):
    # 1351620000001-200050
    video = {
        'Codec': 'H.264',
        'CodecOptions': {
            'Profile': 'baseline',
            'Level': '3',
            'MaxReferenceFrames': '1',
            'InterlacedMode': 'Progressive'
        },
        'KeyframesMaxDist': '90',
        'FixedGOP': 'true',
        'BitRate': '272',
        'FrameRate': 'auto',
        'MaxWidth': '400',
        'MaxHeight': '288',
        'SizingPolicy': 'ShrinkToFit',
        'PaddingPolicy': 'NoPad',
        'DisplayAspectRatio': 'auto',
        'Watermarks': [
            {
                'Id': 'TopLeft',
                'MaxWidth': '10%',
                'MaxHeight': '10%',
                'SizingPolicy': 'ShrinkToFit',
                'HorizontalAlign': 'Left',
                'HorizontalOffset': '10%',
                'VerticalAlign': 'Top',
                'VerticalOffset': '10%',
                'Opacity': '100',
                'Target': 'Content'
            },
            {
                'Id': 'TopRight',
                'MaxWidth': '10%',
                'MaxHeight': '10%',
                'SizingPolicy': 'ShrinkToFit',
                'HorizontalAlign': 'Right',
                'HorizontalOffset': '10%',
                'VerticalAlign': 'Top',
                'VerticalOffset': '10%',
                'Opacity': '100',
                'Target': 'Content'
            },
            {
                'Id': 'BottomLeft',
                'MaxWidth': '10%',
                'MaxHeight': '10%',
                'SizingPolicy': 'ShrinkToFit',
                'HorizontalAlign': 'Left',
                'HorizontalOffset': '10%',
                'VerticalAlign': 'Bottom',
                'VerticalOffset': '10%',
                'Opacity': '100',
                'Target': 'Content'
            },
            {
                'Id': 'BottomRight',
                'MaxWidth': '10%',
                'MaxHeight': '10%',
                'SizingPolicy': 'ShrinkToFit',
                'HorizontalAlign': 'Right',
                'HorizontalOffset': '10%',
                'VerticalAlign': 'Bottom',
                'VerticalOffset': '10%',
                'Opacity': '100',
                'Target': 'Content'
            },
        ]
    }
    audio = {
        'Codec': 'AAC',
        'SampleRate': '44100',
        'BitRate': '128',
        'Channels': '2',
        'CodecOptions': {'Profile': 'AAC-LC'},
    }
    thumbnails = {
        'Format': 'png',
        'Interval': str(interval),
        'MaxWidth': '384',
        'MaxHeight': '216',
        'SizingPolicy': 'ShrinkToFit',
        'PaddingPolicy': 'NoPad',
    }
    response = transcoder_client.create_preset(
        Name=key,
        Description='HLS 400k',
        Container='ts',
        Video=video,
        Audio=audio,
        Thumbnails=thumbnails,
    )
    return response['Preset']['Id']


def delete_transcoder_preset(preset_id):
    response = transcoder_client.delete_preset(
        Id=preset_id,
    )
