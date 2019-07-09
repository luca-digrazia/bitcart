"""
Django settings for mainsite project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import gui
from decouple import Csv, AutoConfig
import redis

config = AutoConfig(search_path="conf")

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUI_DIR = os.path.dirname(os.path.abspath(gui.__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY", default="replaceme")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS_DEFAULT = config(
    "ALLOWED_HOSTS_DEFAULT", default=True, cast=bool)
ALLOWED_HOSTS = []
if ALLOWED_HOSTS_DEFAULT:
    ALLOWED_HOSTS.extend(["localhost", "127.0.0.1", "[::1]"])

ALLOWED_HOSTS_ADD = config("ALLOWED_HOSTS", default="", cast=Csv())
ALLOWED_HOSTS.extend(ALLOWED_HOSTS_ADD)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_dramatiq',
    'rest_framework',
    'rest_framework.authtoken',
    'channels',
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'two_factor',
    'crispy_forms',
    'rest_framework_datatables',
    'corsheaders',
    'drf_yasg',
    'gui'
]

# custom settings
INSTALLED_APPS.extend(config("INSTALLED_APPS", default="", cast=Csv()))

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_datatables.renderers.DatatablesRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework_datatables.filters.DatatablesFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesPageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',

    ],
}

# CORS
CORS_ALLOW_METHODS = (
    'OPTIONS',
)

CORS_ORIGIN_ALLOW_ALL = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

MIDDLEWARE.extend(config("MIDDLEWARE", default="", cast=Csv()))

INTERNAL_IPS = ['127.0.0.1']

if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE = [
        'debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

AUTH_USER_MODEL = "gui.User"

APPEND_SLASH = config("APPEND_SLASH", default=True, cast=bool)
SESSION_EXPIRE_AT_BROWSER_CLOSE = config(
    "SESSION_EXPIRE_AT_BROWSER_CLOSE", default=False, cast=bool)
LOGIN_REDIRECT_URL = config("LOGIN_REDIRECT_URL", default="/")
LOGIN_URL = config("LOGIN_URL", default="/account/login")
ASGI_APPLICATION = "mainsite.routing.application"
ROOT_URLCONF = 'mainsite.urls'
CRISPY_TEMPLATE_PACK = "bootstrap4"

# rpc
RPC_USER = config("RPC_USER", default="electrum")
RPC_PASS = config("RPC_PASS", default="electrumz")

RPC_URL = config("RPC_URL", default="http://localhost:5000/")
# celery
CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="amqp://localhost")
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_RESULT_BACKEND = "rpc://"

# dramatiq
DRAMATIQ_REDIS_URL = config(
    "DRAMATIQ_REDIS_URL", default="redis://127.0.0.1:6379")
DRAMATIQ_BROKER = {
    "BROKER": "dramatiq.brokers.redis.RedisBroker",
    "OPTIONS": {
        "connection_pool": redis.ConnectionPool.from_url(DRAMATIQ_REDIS_URL),
    },
    "MIDDLEWARE": [
        "dramatiq.middleware.AgeLimit",
        "dramatiq.middleware.TimeLimit",
        "dramatiq.middleware.Retries",
        "django_dramatiq.middleware.AdminMiddleware",
        "django_dramatiq.middleware.DbConnectionsMiddleware",
    ]
}


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [config("CHANNEL_LAYERS_HOST", default="redis://localhost")],
        },
    },
}

TEST = config("TEST", cast=bool, default=False)

if not DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': config("CACHE_REDIS_URL", default="redis://127.0.0.1:6379"),
            'OPTIONS': {
                'DB': 0,
                'PARSER_CLASS': 'redis.connection.HiredisParser',
            }
        },
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(GUI_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'gui.context_processors.provide_stats'
            ],
        },
    },
]

WSGI_APPLICATION = 'mainsite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

if not TEST:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config("DB_DATABASE", default="bitcart"),
            'USER': config("DB_USER", default="postgres"),
            'PASSWORD': config("DB_PASSWORD", default="123@"),
            'HOST': config("DB_HOST", default="127.0.0.1"),
            'PORT': config("DB_PORT", default="5432"),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
