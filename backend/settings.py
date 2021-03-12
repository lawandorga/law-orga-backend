"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 2.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2020  Dominik Walser
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>

import os
from datetime import timedelta


def env_true(env_label: str) -> bool:
    if env_label in os.environ and (
        os.environ[env_label] == "1"
        or os.environ[env_label] == "true"
        or os.environ[env_label] == "True"
    ):
        return True
    return False


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
if "SECRET_KEY" in os.environ:
    SECRET_KEY = os.environ.get("SECRET_KEY")
else:
    SECRET_KEY = "srt(vue=+gl&0c_c3pban6a&m2h2iz6mhbx^%^_%9!#-jg0*lz"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env_true("DEBUG")
PROD = env_true("PROD")

if "HOST" in os.environ:
    ALLOWED_HOSTS = ["web", "127.0.0.1", os.environ["HOST"]]
else:
    ALLOWED_HOSTS = ["web", "127.0.0.1"]

if "HOST_IP" in os.environ:
    ALLOWED_HOSTS.append(os.environ["HOST_IP"])

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "backend.api",
    "backend.recordmanagement",
    "backend.files",
    "rest_framework.authtoken",
    "storages",
    "corsheaders",
    "django_prometheus",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "backend.static.middleware.LoggingMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

ROOT_URLCONF = "backend.urls"

# Default settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "backend.api.authentication.ExpiringTokenAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "EXCEPTION_HANDLER": "backend.api.exception_handler.custom_exception_handler",
    "PAGE_SIZE": 100,
}

SILENCED_SYSTEM_CHECKS = ["rest_framework.W001"]

# Authentication Timeout
if env_true("DEV") or env_true("TEST"):
    TIMEOUT_TIMEDELTA = timedelta(weeks=10)
else:
    TIMEOUT_TIMEDELTA = timedelta(minutes=10)

# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = "backend.wsgi.application"

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
if not env_true("LOCAL") and "DB_NAME" in os.environ:
    # remote database
    DATABASES = {
        "default": {
            "ENGINE": "django_prometheus.db.backends.postgresql",
            "NAME": os.environ["DB_NAME"],  # database
            "USER": os.environ["DB_USER"],  # user
            "PASSWORD": os.environ["DB_PASSWORD"],  # password
            "HOST": os.environ["DB_HOST"],  # part of uri, after @ before :, or host
            "PORT": os.environ["DB_PORT"],  # port
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# authentication
AUTH_USER_MODEL = "api.UserProfile"

# E-Mail
# See: https://docs.djangoproject.com/en/dev/topics/email/#smtp-backend
if not env_true("DEV") and "EMAIL_HOST" in os.environ:
    EMAIL_HOST = os.environ["EMAIL_HOST"]
    DEFAULT_FROM_EMAIL = os.environ["EMAIL_ADDRESS"]
    SERVER_EMAIL = os.environ["EMAIL_ADDRESS"]
    EMAIL_PORT = os.environ["EMAIL_PORT"]
    EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]
    EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]
    EMAIL_USER_TLS = os.environ["EMAIL_USER_TLS"]
    EMAIL_USE_SSL = os.environ["EMAIL_USE_SSL"]
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# secret keys
SCW_SECRET_KEY = os.environ.get("SCW_SECRET_KEY")
SCW_ACCESS_KEY = os.environ.get("SCW_ACCESS_KEY")
SCW_S3_BUCKET_NAME = os.environ.get("SCW_S3_BUCKET_NAME")


# Static Files
# See: https://docs.djangoproject.com/en/dev/howto/static-files/
STATICFILES_LOCATION = "static"  # this setting has no effect. in django there doesn't exist this setting?
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static/dist/")]
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "tmp/static/")

# cors
CORS_ALLOWED_ORIGINS = [
    # prod
    "https://law-orga.de",
    "http://law-orga.de",
    "http://www.law-orga.de",
    "https://www.law-orga.de",
    "https://d1g37iqegvaqxr.cloudfront.net",
    # local
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://localhost:3000",
    "http://localhost:3001",
    # dev
    "https://d7pmzq2neb57w.cloudfront.net",
    # test
    "https://d33cushiywgecu.cloudfront.net",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "private-key",
]

# logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"simple": {"format": "%(levelname)s %(message)s"},},
    "handlers": {
        "console": {
            "level": os.environ.get("LOG_LEVEL", "ERROR"),
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "logstash": {
            "level": os.environ.get("LOG_LEVEL", "ERROR"),
            "class": "logstash.TCPLogstashHandler",
            "host": "logstash",
            "port": 5959,
            "version": 1,
            "message_type": "django",
            "fqdn": False,
            "tags": ["django.request", "django", "backend"],
            "formatter": "simple",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["logstash"],
            "level": os.environ.get("LOG_LEVEL", "ERROR"),
            "propagate": True,
        },
        "backend": {
            "handlers": ["console", "logstash"],
            "level": os.environ.get("LOG_LEVEL", "ERROR"),
            "propagate": True,
        },
    },
}
