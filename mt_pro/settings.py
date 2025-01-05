"""
Django settings for mt_pro project.
"""

import os
from logging import info as log_info, error as log_error
from pathlib import Path

from kubernetes import config
from kubernetes.config.config_exception import ConfigException
from pymongo import MongoClient

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-ayyh^la1^^=j2vk16u@*9nj%^d5%ca)9nk_rrl^2$5$fl9-7$n"

DEBUG = True

ALLOWED_HOSTS = ["localhost", ".localhost", "127.0.0.1", "status"]
CSRF_TRUSTED_ORIGINS = ["http://status", "http://localhost", "http://127.0.0.1"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "mt_app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mt_pro.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "static/templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "mt_pro.wsgi.application"
ASGI_APPLICATION = "mt_pro.routing.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "state_manager",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": f'{os.getenv("DB_HOST", "localhost")}',
        "PORT": 5432,
        "OPTIONS": {"options": f'-c search_path={os.getenv("DB_SCHEMA", "public")}'},
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "edit_static"),
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "mt_app.CustomUser"
LOGIN_REDIRECT_URL = "/admin/"
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, 6379)],  # Redis server configuration
        },
    },
}

# CELERY STUFF
BROKER_URL = f"redis://{REDIS_HOST}:6379/1"
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:6379/1"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# MongoDB Connection
MONGO_DB_NAME = "main"
MONGO_URI = (
    f"mongodb://{os.getenv('MONGO_USER', 'mongo')}:{os.getenv('MONGO_PASSWORD', 'mongo1234')}@"
    f"{os.getenv('MONGO_HOST', 'localhost')}:{os.getenv('MONGO_PORT', '27017')}/"
)

# MongoDB Client
MONGO_CLIENT = MongoClient(MONGO_URI)
MONGO_DB = MONGO_CLIENT[MONGO_DB_NAME]


def load_k8s_config():
    # loading kubernetes config
    try:
        config.load_incluster_config()
        log_info("loaded dev cluster k8 config.")
    except ConfigException:
        try:
            config.load_kube_config()
            log_info("loaded local cluster k8 config.")
        except ConfigException:
            log_error("No k8 config found")


# load kube config
load_k8s_config()
