import uuid
import json
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
import pytz


loc_tz = pytz.timezone(settings.TIME_ZONE)

# Create your models here.


def jwt_get_secret_key(user_model):
    return settings.SECRET_KEY + str(user_model.jwt_secret)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, password, **extra_fields)


class User(AbstractUser):
    jwt_secret = models.UUIDField(default=uuid.uuid4)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    objects = UserManager()

    def change_jwt_secret(self):
        self.jwt_secret = uuid.uuid4()

    def created_str(self):
        return self.created.strftime('%Y/%m/%d %H:%M')

    def get_delete_form(self):
        from .forms import DeleteUser
        return DeleteUser(initial={'username': self.username})


class Location(models.Model):
    name = models.CharField(
        max_length=300, default='', verbose_name="ロケーション名")
    is_active = models.BooleanField(default=True)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created"]

    def created_str(self):
        created = self.created.astimezone(loc_tz)
        return created.strftime('%Y/%m/%d %H:%M')

    def get_delete_form(self):
        from .forms import DeleteLocation
        return DeleteLocation(initial={'location_id': self.pk})


class State(models.Model):
    CHOICES = ((0, '処理中'), (1, '正常'), (2, '異常'), )
    STATE_CSS_CLASS = {
        0: 'work-state',    # 処理中
        1: 'normal-state',  # 正常
        2: 'fault-state',   # 異常
    }
    state_type = models.IntegerField(choices=CHOICES)
    state_list = models.TextField(default='')
    updated_state_list = models.TextField(default='')
    location = models.ForeignKey('Location', related_name='state_location', blank=True, null=True,
                                 on_delete=models.SET_NULL)
    movie_url = models.URLField(default='')
    thumb_url = models.URLField(default='')
    fps = models.FloatField(default=1.0)
    update_time = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-update_time"]

    @classmethod
    def get_first_state(cls):
        return cls.objects.all().first()

    def set_state_list(self, value):
        self.state_list = json.dumps(value)

    def get_state_list(self):
        return json.loads(self.state_list)

    def set_updated_state_list(self, value):
        self.updated_state_list = json.dumps(value)

    def get_updated_state_list(self):
        return json.loads(self.updated_state_list)

    def get_state_bar_data(self):
        def calc_width(start, end):
            return (end - start) / total_sec * max_width
        if self.updated_state_list:
            state_list = self.get_updated_state_list()
        else:
            state_list = self.get_state_list()
        total_sec = state_list[-1]['end']
        max_width = 1095
        return [{'width': calc_width(d['start'], d['end']),
                 'color': 'indianred' if d['status'] else 'aquamarine'} for d in state_list]

    def get_state_css_class(self):
        return self.STATE_CSS_CLASS[self.state_type]

    def get_thumb_url_list(self):
        if not self.thumb_url:
            return []
        url_format = self.thumb_url.replace('_00001.png', '')
        url_format += '_{:05d}.png'
        return [url_format.format(i+1) for i in range(settings.THUMBNAIL_SEP_COUNT)]

    def get_state_list_json(self, dump=True):
        def get_current_state(index):
            current_sec = total_sec / settings.THUMBNAIL_SEP_COUNT * index
            for index, d in enumerate(state_list):
                if d['start'] <= current_sec <= d['end']:
                    return index, d

        def calc_hour_minute_sec(sec):
            hour = sec // (60 * 60)
            minute = sec % (60 * 60) // 60
            sec = sec % (60 * 60) % 60
            return int(hour), int(minute), int(sec)

        if not self.thumb_url:
            return json.dumps({})

        if self.updated_state_list:
            state_list = self.get_updated_state_list()
        else:
            state_list = self.get_state_list()
        total_sec = state_list[-1]['end']
        results = {
            'thumb_state': {},
            'state_list': {},
            'state_bar_data': self.get_state_bar_data(),
        }
        for i, d in enumerate(state_list):
            start_hour, start_minutes, start_sec = calc_hour_minute_sec(d['start'])
            end_hour, end_minutes, end_sec = calc_hour_minute_sec(d['end'])
            state_type = 2 if d['status'] else 1
            state_type_display = self.CHOICES[state_type][1]
            reason = ''
            if d.get('reason') and state_type == 2:
                try:
                    reason_object = Reason.objects.get(pk=int(d['reason']))
                    reason = reason_object.reason
                except ObjectDoesNotExist:
                    # 存在しなければ空欄
                    pass
            results['state_list'][i] = {
                'index': i,
                'start': d['start'],
                'end': d['end'],
                'start_hour': start_hour,
                'start_minutes': start_minutes,
                'start_sec': start_sec,
                'end_hour': end_hour,
                'end_minutes': end_minutes,
                'end_sec': end_sec,
                'state_type': state_type,
                'state_css_class': self.STATE_CSS_CLASS[state_type],
                'state_type_display': state_type_display,
                'reason': reason,
            }
        for i in range(settings.THUMBNAIL_SEP_COUNT):
            current_state_index, current_state = get_current_state(i)
            seek_sec = total_sec / settings.THUMBNAIL_SEP_COUNT * i
            results['thumb_state'][i+1] = {
                'state_list_index': current_state_index,
                'seek_sec': seek_sec,
            }
        if dump:
            return json.dumps(results)
        return results

    def update_state(self, index, start_hour, start_minutes, start_sec, end_hour, end_minutes, end_sec,
                     status_type, reason):
        if self.updated_state_list:
            state_list = self.get_updated_state_list()
        else:
            state_list = self.get_state_list()
        # 秒に変換
        start = start_hour * (60 * 60)
        start += start_minutes * 60
        start += start_sec
        end = end_hour * (60 * 60)
        end += end_minutes * 60
        end += end_sec
        # 値更新
        state_list[index]['start'] = start
        state_list[index]['end'] = end
        state_list[index]['status'] = False if int(status_type) == 1 else True
        state_list[index]['reason'] = reason
        # 整合性チェック
        results = []
        before_data = None
        for i, data in enumerate(state_list):
            if i == 0:
                # 初めの開始時間は0のはず
                if data['start'] != 0:
                    data['start'] = 0
                results += [data]
                before_data = data
            else:
                # 直前の状態と同じだったら結合する
                if data['status'] == before_data['status']:
                    before_data['end'] = data['end']
                # 直前の終了時間を過ぎているので削除
                elif data['end'] <= before_data['end']:
                    continue
                else:
                    # 直前の終了時間と開始時間を合わせる
                    if data['start'] != before_data['end']:
                        data['start'] = before_data['end']
                    results += [data]
                    before_data = data
        # データ更新
        self.set_updated_state_list(results)

    def to_dict(self):
        return {
            'state_type': self.state_type,
            'state_type_val': self.get_state_type_display(),
            'movie_url': self.movie_url,
            'location_id': self.location_id,
            'created': self.created_str(),
            'update_time_str': self.update_time_str(),
        }

    def created_str(self):
        created = self.update_time.astimezone(loc_tz)
        return created.strftime('%Y/%m/%d %H:%M')

    def update_time_str(self):
        update_time = self.update_time.astimezone(loc_tz)
        return update_time.strftime('%Y/%m/%d %H:%M')


class Reason(models.Model):
    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    reason = models.CharField(max_length=255, blank=False, null=False)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created"]

    @classmethod
    def get_choices_list(cls, location_id):
        return [(0, '')] + [(r.pk, r.reason) for r in cls.objects.filter(location_id=location_id)]

    def created_str(self):
        return self.created.strftime('%Y/%m/%d %H:%M')

    def get_delete_form(self):
        from .forms import DeleteReasonForm
        return DeleteReasonForm(initial={'reason_id': self.pk})
