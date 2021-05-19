import os
from app.celery import app
from app.utils import s3_upload, s3_upload_obj


@app.task()
def s3_upload_task(bucket_name, save_filename, file_path):
    s3_upload(bucket_name, file_path, save_filename)
    os.remove(file_path)


@app.task()
def s3_upload_obj_task(bucket_name, file, file_name):
    s3_upload_obj(bucket_name, file_name, file)
