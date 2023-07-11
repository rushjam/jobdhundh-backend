from pathlib import Path
import os
from dotenv import load_dotenv
import logging.config
# Load environment variables from the .env file.
load_dotenv()
from datetime import timedelta

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}
logging.config.dictConfig(LOGGING)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# 📁 webappexample/settings.py -----




# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False") == "True"


ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')



# Application definition

INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'jobs',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'rest_auth.registration',
]
# Django Rest Framework handles this by providing a set of authentication classes which can be used instead. If you are using token-based authentication (such as the one provided by Django Rest Auth), CSRF protection can be safely turned off for the API views.
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler'
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}



SITE_ID = 1
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']

CORS_ORIGIN_ALLOW_ALL = os.getenv("CORS_ORIGIN_ALLOW_ALL", "False") == "True"
CORS_ORIGIN_WHITELIST = os.getenv("CORS_ORIGIN_WHITELIST")


ROOT_URLCONF = 'jobscrape_project.urls'

# Add the following line after 'BASE_DIR = ...'
TEMPLATE_DIR = os.path.join(BASE_DIR, "webappexample", "templates")

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
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

WSGI_APPLICATION = 'jobscrape_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Check the environment.
environment = os.getenv('DJANGO_ENVIRONMENT')

if environment == 'production':
    # Use production database settings.
    DATABASES = {
        'default': {
            'ENGINE': os.getenv('PROD_DB_ENGINE'),
            'NAME': os.getenv('PROD_DB_NAME'),
            'USER': os.getenv('PROD_DB_USER'),
            'PASSWORD': os.getenv('PROD_DB_PASSWORD'),
            'HOST': os.getenv('PROD_DB_HOST'),
            'PORT': os.getenv('PROD_DB_PORT'),
        }
    }
else:
    # Use development database settings.
    DATABASES = {
        'default': {
            'ENGINE': os.getenv('DEV_DB_ENGINE'),
            'NAME': os.getenv('DEV_DB_NAME'),
            'USER': os.getenv('DEV_DB_USER'),
            'PASSWORD': os.getenv('DEV_DB_PASSWORD'),
            'HOST': os.getenv('DEV_DB_HOST'),
            'PORT': os.getenv('DEV_DB_PORT'),
        }
    }




# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")

# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_HTTPONLY = True


SESSION_COOKIE_AGE = 10800  # Three day
SESSION_SAVE_EVERY_REQUEST = True