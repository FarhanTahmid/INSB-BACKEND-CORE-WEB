"""
Django settings for insb_port project.

Generated by 'django-admin startproject' using Django 4.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
from celery.schedules import crontab
import os
# import dj_database_url
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/
from dotenv import load_dotenv
import os
load_dotenv()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
if(os.environ.get('SETTINGS')=='dev'):
    DEBUG = True
else:
    DEBUG = False

if(os.environ.get('SETTINGS')=='dev'):
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = ['ieeensusb.org','portal.ieeensusb.org']


LOGIN_URL='/portal/users/login'

# Application definition

INSTALLED_APPS = [
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'central_branch',
    'membership_development_team',
    'port',
    'users',
    'system_administration',
    'recruitment',
    'api',
    'logistics_and_operations_team',
    'events_and_management_team',
    'public_relation_team',
    'meeting_minutes',
    'main_website',
    'content_writing_and_publications_team',
    'promotions_team',
    'website_development_team',
    'media_team',
    'graphics_team',
    'finance_and_corporate_team',
    # 'ieee_nsu_sb_pes_sbc',
    # 'ieee_nsu_sb_ras_sbc',
    'ckeditor',
    'chapters_and_affinity_group',
    'central_events',
    'django_celery_beat',
    'django_celery_results',
]

MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'main_website.middleware.BlockMainWebMiddleWare',
]

ROOT_URLCONF = 'insb_port.urls'
import os
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
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

WSGI_APPLICATION = 'insb_port.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases


if(os.environ.get('SETTINGS')=='dev'):
    DATABASES = {
        'default': {
                    
            #Postgres in localhost
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DEV_DATABASE_NAME'),
            'USER': os.environ.get('DEV_DATABASE_USER'),
            'PASSWORD': os.environ.get('DEV_DATABASE_PASSWORD'),
            'HOST': os.environ.get('DEV_DATABASE_HOST'),
            'PORT':'', 
            

        }
    }
if(os.environ.get('SETTINGS')=='prod'):
    DATABASES = {
        
        # MySQL in Production
        'default': {
            
            'ENGINE': 'django.db.backends.mysql', 
            'NAME': os.environ.get('PROD_DATABASE_NAME'),
            'USER': os.environ.get('PROD_DATABASE_USER'),
            'PASSWORD': os.environ.get('PROD_DATABASE_PASSWORD'),
            'HOST': 'localhost',
            'PORT': '3306',
            
        }
        
    }

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

from django.utils import timezone
TIME_ZONE = 'Asia/Dhaka'
USE_TZ = True

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/


STATIC_URL = 'static/'
#static directory
STATIC_ROOT=os.path.join(BASE_DIR,'staticfiles')
STATICFIlES_DIRS=(os.path.join(BASE_DIR,'static/'))
    


#TEMPLATE_DIRS=(os.path.join(os.path.dirname(__file__) ,'../Templates').replace('\\','/'))

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#Date input Formats in the models
DATE_INPUT_FORMATS = ['%d-%m-%Y']



#Media Files
MEDIA_ROOT= os.path.join(BASE_DIR, 'User Files/')
MEDIA_URL= "/media_files/" 

#to do user login required
# LOGIN_REDIRECT_URL='users:dashboard'
LOGOUT_REDIRECT_URL='users:logoutUser'
LOGIN_URL='users:login'


REST_FRAMEWORK={
    'DEFAULT_RENDERER_CLASSES':('rest_framework.renderers.JSONRenderer',)
}

handler404='central_branch.views.custom_404'
handler500='central_branch.views.custom_500'

#EMAIL SETTINGS
EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST='mail.ieeensusb.org'
EMAIL_PORT='465'
EMAIL_HOST_USER=os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD=os.environ.get('EMAIL_PASSWORD')
EMAIL_USE_SSL = True
EMAIL_USE_TLS=False

# RESIZING IMAGE
DJANGORESIZED_DEFAULT_SIZE = [1920, 1080]
DJANGORESIZED_DEFAULT_SCALE = 1.0
DJANGORESIZED_DEFAULT_QUALITY = 80
DJANGORESIZED_DEFAULT_KEEP_META = True
DJANGORESIZED_DEFAULT_NORMALIZE_ROTATION = True

CELERY_BROKER_URL = "amqps://mrhkupcx:Es-Dd6MKxkwapnb1zMlwybTaYGwflFLB@lionfish.rmq.cloudamqp.com/mrhkupcx"
CELERY_RESULT_BACKEND = "django-db"
CELERY_RESULT_EXTENDED = True
CELERY_TASK_SERIALIZER = 'json'
# CELERY_BEAT_SCHEDULE = {
#     # "active_inactive_member_status_task":{
#     #     "task":"users.tasks.running_task",
#     #     "schedule":crontab(minute=0,hour=0),
#     # },
#     # "sending_email_task":{
#     #     "task":"users.tasks.sending_email",
#     #     "schedule":60,
#     # },
# }

NEWS_API_KEY=os.environ.get('NEWS_API_KEY')