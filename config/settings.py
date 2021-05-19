"""
Django settings for water_abnormality_server project.

Generated by 'django-admin startproject' using Django 2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

ENV_FILE = os.path.join(BASE_DIR, '.env')
if os.path.exists(ENV_FILE):
    load_dotenv(ENV_FILE)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', '')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.environ.get('DEBUG', 0)))

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_results',
    'bootstrap3',
    'bootstrap_datepicker_plus',
    'debug_toolbar',
    'app.apps.AppConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'builtins': [
                'bootstrap3.templatetags.bootstrap3',
            ],
        },
    },
]

BOOTSTRAP3 = {
    'formset_renderers': {
        'default': 'bootstrap3.renderers.FormsetRenderer',
        'tabular': 'app.django-bootstrap3-tabular.ConcordiaFormsetRenderer',
    },
    'field_renderers': {
        'default': 'bootstrap3.renderers.FieldRenderer',
        'inline': 'bootstrap3.renderers.InlineFieldRenderer',
        'tabular': 'app.django-bootstrap3-tabular.ConcordiaFieldRenderer',
    },
}

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default':  {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_DATABASE'),
        'HOST': os.environ.get('MYSQL_HOST'),
        'USER': os.environ.get('MYSQL_USER'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD'),
        'OPTIONS': {
            'init_command': 'SET sql_mode=STRICT_TRANS_TABLES',
            'charset': 'utf8mb4',
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'


INTERNAL_IPS = ['127.0.0.1']

AUTH_USER_MODEL = 'app.User'

LOGIN_REDIRECT_URL = '/'

# logging
if not DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'production': {
                'format': '%(asctime)s [%(levelname)s] %(process)d %(thread)d %(pathname)s %(lineno)d %(message)s'
            },
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'production',
            },
        },
        'loggers': {
            '': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False,
            },
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    }

# django-celery-results
CELERY_BROKER_URL = "redis://redis:6379/1"
CELERY_RESULT_BACKEND = 'django-db'
DJANGO_CELERY_RESULTS_TASK_ID_MAX_LENGTH = 191

# 推論用設定
# 一時ファイル置き場
DOWNLOAD_PATH = 'tmp/movie'
IMAGES_PATH = 'tmp/images'
SAVE_PATH = 'tmp/save'
# 元動画を置くS3バケット名
UPLOAD_S3_BUCKET_NAME = os.environ.get('UPLOAD_S3_BUCKET_NAME')
# 推論動画を置くS3バケット名
SAVE_S3_BUCKET_NAME = os.environ.get('SAVE_S3_BUCKET_NAME')
# ロケーションの初期値
LOCATION = 1
# 推論動画のサムネイル数
THUMBNAIL_SEP_COUNT = 30
# 動画作成用の設定
FOURCC = 'mp4v'
FONT = 'font/ipagp.ttf'
FONT_SIZE = 60
NORMAL_TEXT = ('正常', (255, 0, 0))
FAULT_TEXT = ('異常', (0, 0, 255))
IMAGE_SIZE = (640, 360)
TEXT_POS = (500, 290)
LINE_WIDTH = 10
SEGMENT_DURATION = '10'
# 推論環境のパス
PREDICTION_PATH = os.path.join(BASE_DIR, 'detection', 'models')
