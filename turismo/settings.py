import os

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

env_vars = open(str(BASE_DIR.parent) + "/.envvar", "r")

env = []
for linha in env_vars:
    env.append(linha.rstrip())

db_name = env[0]
db_user = env[1]
db_passwd = env[2]
SECRET_KEY = env[3]
debug = env[4]
email_user = env[5]
email_pass = env[6]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = eval(debug)

ALLOWED_HOSTS = ['turismo.jlb.net.br', 'senhas.novafriburgo.rj.gov.br', '127.0.0.1', '127.0.1.1', 'localhost', '192.168.1.109']

try:
    RECAPTCHA_PUBLIC_KEY = env[7]
    RECAPTCHA_PRIVATE_KEY = env[8]
except:
    RECAPTCHA_PUBLIC_KEY = ''
    RECAPTCHA_PRIVATE_KEY = ''
# Application definition

INSTALLED_APPS = [
    'senhas.apps.SenhasConfig',
    'equipamentos.apps.EquipamentosConfig',
    'contas.apps.ContasConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'qr_code',
    'guias',
    'report',
    'social_django'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

try:
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env[9]
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env[10]

    SOCIAL_AUTH_FACEBOOK_KEY = env[11]
    SOCIAL_AUTH_FACEBOOK_SECRET = env[12]
except:
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ''
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ''

    SOCIAL_AUTH_FACEBOOK_KEY = ''
    SOCIAL_AUTH_FACEBOOK_SECRET = ''


ROOT_URLCONF = 'turismo.urls'

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
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'turismo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',

        'NAME': db_name,
        'PORT': '',

        'USER': db_user,
        'PASSWORD': db_passwd,
        'HOST': '127.0.0.1',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATIC_URL = '/static/'
# STATIC_ROOT = '/home/turismo/site/turismo/equipamentos/static'
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

LOGIN_URL='/login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = '/contas/sair'
LOGOUT_REDIRECT_URL = '/login'

# JLB para SSL

MIDDLEWARE_CLASSES = (
    'sslify.middleware.SSLifyMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = 'Secretaria Municipal de Turismo e Marketing <turismo@sme.novafriburgo.rj.gov.br>'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = email_user
EMAIL_HOST_PASSWORD = email_pass
