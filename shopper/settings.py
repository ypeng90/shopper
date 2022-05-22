"""
Django settings for shopper project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from shopper.secret import SECRET_KEY, \
    USERNAME_DATABASE, PASSWORD_DATABASE, NAME_DATABASE, \
    USERNAME_RABBITMQ, PASSWORD_RABBITMQ, VHOST_RABBITMQ, \
    USERNAME_REDIS, PASSWORD_REDIS, DB_REDIS


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = {imported}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "account",
    "product",
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

ROOT_URLCONF = "shopper.urls"

TEMPLATES = [
    {
        "BACKEND": 'django.template.backends.django.DjangoTemplates',
        "DIRS": [],
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

WSGI_APPLICATION = "shopper.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

# setup users
# CREATE TABLE users
# (
#     userid int NOT NULL,
#     username varchar(20) NOT NULL UNIQUE,
#     password char(64) NOT NULL,
#     salt char(4) NOT NULL,
#     reg_date datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
#     PRIMARY KEY (userid)
# );
#
# setup products
# CREATE TABLE products
# (
#     userid int NOT NULL,
#     sku varchar(15) NOT NULL,
#     name varchar(64) NOT NULL,
#     store char(3) NOT NULL,
#     track int NOT NULL DEFAULT 1,
#     PRIMARY KEY (userid, sku, store)
# );
#
# setup inventory
# CREATE TABLE inventory
# (
#     sku varchar(15) NOT NULL,
#     quantity int NOT NULL,
#     store char(3) NOT NULL,
#     store_id varchar(8) NOT NULL,
#     check_time datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
#     PRIMARY KEY (sku, store, store_id)
# );
#
# setup zipcode_stores_mapping
# CREATE TABLE zipcode_stores_mapping
# (
#     store char(3) NOT NULL,
#     zipcode char(5) NOT NULL,
#     store_id varchar(8) NOT NULL,
#     PRIMARY KEY (store, zipcode, store_id)
# );
#
# setup stores
# MySQL uses POINT(lat, long)
# GeoJSON uses "coordinates": [long, lat]
# CREATE TABLE stores
# (
#     store char(3) NOT NULL,
#     store_id varchar(8) NOT NULL,
#     store_name varchar(48) NOT NULL,
#     address varchar(96) NOT NULL,
#     city varchar(24) NOT NULL,
#     state varchar(24) NOT NULL,
#     zipcode char(5) NOT NULL,
#     location POINT NOT NULL SRID 4326,
#     PRIMARY KEY (store, store_id)
# );
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": NAME_DATABASE,
        "HOST": "localhost",
        "PORT": 3306,
        "USER": USERNAME_DATABASE,
        "PASSWORD": PASSWORD_DATABASE,
        "CHARSET": "utf8",
    }
}
# Migrate after setting models.
# python manage.py makemigrations
# python manage.py migrate

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "static/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "product", "static"),
    os.path.join(BASE_DIR, "account", "static"),
]

# To easily get csrftoken for fetch.
# Include {% csrf_token %} in html,
# Add 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value into headers
CSRF_USE_SESSIONS = True

# Celery Configuration Options.
# # Assuming RabbitMQ and Redis are running, run these
# # commands in order.
# python manage.py runserver
# celery -A shopper worker -l info
# # Only if using beat for scheduling, such as handling
# # result_expires.
# celery -A shopper beat -l info ...

# Let celery use TIME_ZONE, otherwise setting expires
# might cause immediate revoking.
CELERY_TIMEZONE = TIME_ZONE

# Overall soft time limit: 9 minutes. SoftTimeLimitExceeded
# exception will be raised so that certain procedure can
# be executed before task is killed. Can be specified per
# task.
CELERY_TASK_SOFT_TIME_LIMIT = 9 * 60
# Overall hard time limit: 10 minutes. The task will be
# killed then. Can be specified per task.
CELERY_TASK_TIME_LIMIT = 10 * 60

# Disable prefetching.
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

# Run synchronously for testing and debugging.
# CELERY_TASK_ALWAYS_EAGER = True

# "transport://username:password@hostname:port/virtual_host"
CELERY_BROKER_URL = "amqp://{}:{}@localhost:5672/{}".format(
    USERNAME_RABBITMQ,
    PASSWORD_RABBITMQ,
    VHOST_RABBITMQ
)
# "redis://username:password@hostname:port/db"
CELERY_RESULT_BACKEND = "redis://{}:{}@localhost:6379/{}".format(
    USERNAME_REDIS,
    PASSWORD_REDIS,
    DB_REDIS
)
# A built-in periodic task will delete the results
# after this time (celery.backend_cleanup), assuming
# that celery beat is enabled. The task runs daily
# at 4am.
CELERY_RESULT_EXPIRES = 12 * 60 * 60

# Setup queues manually.
# Not needed if CELERY_TASK_CREATE_MISSING_QUEUES
# is True (by default).
# celery -A shopper worker -l info -> [queues]: celery
# celery -A shopper worker -l info -Q fast -> [queues]: fast
# CELERY_TASK_QUEUES = {
#     "fast": {
#         "exchange": "fast",
#         "routing_key": "fast",
#     },
#     "slow": {
#         "exchange": "slow",
#         "routing_key": "slow",
#     },
# }
# When manual CELERY_TASK_QUEUES is set, things change.
# celery -A shopper worker -l info
#   -> [queues]: fast and slow
# celery -A shopper worker -l info -Q fast
#   -> [queues]: fast
CELERY_TASK_QUEUES = {
    # The default queue for tasks is celery. Either keep
    # it or set CELERY_TASK_DEFAULT_QUEUE = "fast"
    "celery": {
        "exchange": "celery",
        "routing_key": "celery",
    },
    "fast": {
        "exchange": "fast",
        "routing_key": "fast",
    },
    "slow": {
        "exchange": "slow",
        "routing_key": "slow",
    },
}
# celery -A shopper worker -l info
#   -> [queues]: celery, fast and slow
