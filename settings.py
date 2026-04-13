# Django settings for sermepa project.

DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'sermepa.db',
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

TIME_ZONE = 'Europe/Madrid'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

USE_TZ = True

MEDIA_ROOT = ''

MEDIA_URL = ''

SECRET_KEY = '^(k%_6b(l&$w)v8rx+6*vk!4qi)czzfxdas5&08uwr6)af_4xs'

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'urls'

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

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'sermepa',
    'sermepa_test',
    'django.contrib.admin',
)

SERMEPA_URL_PRO = 'https://sis.redsys.es/sis/realizarPago'
SERMEPA_URL_TEST = 'https://sis-t.redsys.es:25443/sis/realizarPago'
SERMEPA_MERCHANT_CODE = '999008881'  # Redsys official test merchant
SERMEPA_TERMINAL = '001'
SERMEPA_SECRET_KEY = 'sq7HjrUOBfKmC576ILgskD5srU870gJ7'
SERMEPA_BUTTON_IMG = '/site_media/_img/targets.jpg'
SERMEPA_CURRENCY = '978'
SERMEPA_SIGNATURE_VERSION = 'HMAC_SHA256_V1'