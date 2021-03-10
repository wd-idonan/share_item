"""
Django settings for wd_shangmi project.

Generated by 'django-admin startproject' using Django 1.11.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '($@w8w3gob5yqa#y+9ul!3^%)(v3a3mruxua!0sta%fzdd&f!g'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shangmi_v1',
    'rest_framework'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'wd_shangmi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'wd_shangmi.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': "myshangmi",
        'PORT':3306,
        "HOST": "localhost",
        "USER": "root",
        "PASSWORD": "root936594"

    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

# 微信小程序第三方接口获取openid
SMALL_WEIXIN_OPENID_URL = "https://api.weixin.qq.com/sns/jscode2session"

# redis缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        # 缓存地址
        "LOCATION": "redis://127.0.0.1:6379/8",
        "OPTIONS": {
            'MAX_ENTRIES': 2000,
            # 使用线程池管理连接
            "CONNECTION_POOL_KWARGS": {"max_connections": 100},
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    'user': {
        'BACKEND': 'django_redis.cache.RedisCache',
        # 缓存地址
        "LOCATION": "redis://127.0.0.1:6379/12",
        "OPTIONS": {
            'MAX_ENTRIES': 2000,
            # 使用线程池管理连接
            "CONNECTION_POOL_KWARGS": {"max_connections": 100},
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

USER_TOKEN_LIFE = 60*60*24*15  # 15天

# 短信接口发验证码
REGION_ID = "cn-hangzhou"
ACCESS_KEY_ID = "111"
ACCESS_KEY_SECRET = "222"
DOMAIN = "www.aliyuncs.com"
# 签名
SIGN_NAME = "idonan"
# 短信模板
TEMPLATE_NAME = "SMS_170181103"