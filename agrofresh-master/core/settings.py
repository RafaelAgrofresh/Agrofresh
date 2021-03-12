import os
from decouple import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_1122')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool, default=False)


# load production server from .env
ALLOWED_HOSTS = [
    'localhost', '127.0.0.1',
    config('SERVER', default='127.0.0.1'),
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Application definition
INSTALLED_APPS = [
    'core',
    'authentication.apps.Config',
    'alerts.apps.Config',
    'api.apps.Config',
    'cold_rooms.apps.Config',
    'historical.apps.Config',
    'comms.apps.Config',
    'dbinfo.apps.Config',
    'custom_widgets',
    'd3',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',     # pip install django-crispy-forms
    'adminsortable2',   # pip install django-admin-sortable2
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

ROOT_URLCONF = 'core.urls'
LOGIN_URL = "login"
LOGOUT_URL = "logout"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"
TEMPLATE_DIR = os.path.join(BASE_DIR, "core/templates")  # ROOT dir for templates

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
                'comms.context_processors.struct_fields',
                'historical.context_processors.settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi:application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }
    'default': {
        'ENGINE': 'timescale.db.backend',
        'NAME': config('DB_NAME', default='agrofresh'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASS', default='password'),
        'HOST': config('DB_HOST', default='127.0.0.1'),
        'PORT': config('DB_PORT', cast=int, default=5432),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators
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

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/
# https://samulinatri.com/blog/django-translation/#introduction

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]
LANGUAGE_CODE = 'es'
LANGUAGES = [
    ('en-EN', 'English'),
    ('es', 'Español'),
]

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Europe/Madrid'
# https://docs.djangoproject.com/en/3.0/topics/i18n/timezones/#default-time-zone-and-current-time-zone

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'core/static'),
)

INTERNAL_IPS = [
    '127.0.0.1',
]

COMMS_TASK_PERIOD = 1

# Email configuration
EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST=config('EMAIL_HOST')
EMAIL_HOST_USER=config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD=config('EMAIL_HOST_PASSWORD')
EMAIL_PORT=config('EMAIL_PORT', cast=int, default=587)
EMAIL_USE_TLS=config('EMAIL_USE_TLS', cast=bool, default=True)
EMAIL_USE_SSL=config('EMAIL_USE_SSL', cast=bool, default=False)
