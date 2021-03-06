from __future__ import absolute_import
"""
Django settings for CMDB project.

Generated by 'django-admin startproject' using Django 1.9.8.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'nbyv#ob%@3@9214+!6n31_)4c08-@%45n5*mb7*$el7jl2#s!^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
APPEND_SLASH = False

ALLOWED_HOSTS = ['*',]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'arya.apps.AryaConfig',
    'corsheaders',
    'rbac',
    'app01',
    'db',
    'release',
    'clientapi',
    'rest_framework',
    'djcelery',
    'VueApi',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'rbac.middlewares.rbac.RbacMiddleware',
]

ROOT_URLCONF = 'CMDB.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'CMDB.wsgi.application'
DATA_UPLOAD_MAX_MEMORY_SIZE = 10000000000

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cmdb',
        'USER': 'cmdb_user',
        'PASSWORD': 'onda1478963',
        'HOST': '192.168.18.102',
        'PORT': '3306',
    }
}

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'
# TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False
# USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "arya/static"),
)

####################配置变量###############
PERMISSION_URL_DICT_KEY='dafsessiondfd'

VALID_URL=('/arya/login/','/arya/register/','/arya/logout/',
           '/arya/ali_client_api.html/','/arya/ali_main.html/',
           '/arya/ali_func.html/','/arya/alirds_func.html/',
           '/arya/celery_status.html/','/log/',
           '/arya/alirds_client_api.html/','/arya/db_func.html/',
            '/arya/sendmail/','/arya/home/','/package/','/test.html',
            '/code.html','/api/release/','/static/','/admin/*','/api/auth/',
           '/vueapi','/test'
           )

SESSION_COOKIE_AGE=60*60*3   #session 保存时间，3小时
SESSION_EXPIRE_AT_BROWSER_CLOSE=True
CODEIMG='fsadcodef'
USER='userresu'
USERID='idusersuid'
PERMISSION_HOST='fdasfqw'
PTEAM_OBJ='fdasfaegth'
PERMISSION_MENU_KEY='dfadfew'
PERMISSION_AUTH_KEY='dfadsfqwew'
HTTP_URL='http://127.0.0.1:8000'
# HTTP_URL='http://10.45.138.187'
LOG_PATH=(
    os.path.join(BASE_DIR, "log/error.log"),
    os.path.join(BASE_DIR, "log/password.log"),
    os.path.join(BASE_DIR, "log/release_api.log"),
)



#######ali_api
ACCESSKEY_ID='LTAIH9CwyQbfA0h3'
ACCESSKEY_KEY='lY8NnmUIFpfyYFXRs3IHVXhC2Ou6tZ'





###########restframework
REST_FRAMEWORK = {
    # "DEFAULT_VERSIONING_CLASS":"rest_framework.versioning.URLPathVersioning",
    # 'ALLOWED_VERSIONS':['v1','v2'],
    # "DEFAULT_VERSION":'v1',

    "UNAUTHENTICATED_USER":None,
    "UNAUTHENTICATED_TOKEN":None,
    # "UNAUTHENTICATED_USER":lambda :None,
    # "UNAUTHENTICATED_TOKEN":lambda :None,
    'DEFAULT_AUTHENTICATION_CLASSES': ['release.utlis.api_auth.TokenAuthtication',]
}

#跨域增加忽略
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = ()

CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'VIEW',
)
# CORS_ALLOW_HEADERS = ('*')
CORS_ALLOW_HEADERS = (
    'content-disposition',
    'accept',
    'accept-encoding',
    'authorization',
    'Authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
)


#################client################
# SALT_API='https://101.201.141.232:8001/'
# SALT_USERNAME='saltapi'
# SALT_PASSWORD='qqqqq'


########celery
import djcelery
from celery.schedules import crontab
from datetime import timedelta
djcelery.setup_loader()
CELERY_TIMEZONE = TIME_ZONE
BROKER_URL='redis://:onda@10.0.0.1:6379/1'
CELERY_RESULT_BACKEND='redis://:onda@10.0.0.1:6379/2'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Nairobi'
CELERY_IMPORTS=['app01.task','clientapi.task']
CELERYD_MAX_TASKS_PER_CHILD = 3
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

