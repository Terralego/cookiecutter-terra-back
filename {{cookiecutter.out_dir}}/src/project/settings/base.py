"""
Django settings

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""
import os
from datetime import timedelta
from importlib import import_module

INSTALLED_APPS = ()
CUSTOM_APPS = (
    'terracommon.core',
    'terracommon.accounts',
    'terracommon.terra',
    'terracommon.trrequests',
    'terracommon.data_importers',
    'terracommon.document_generator',
    'terracommon.events',
    'terracommon.datastore',
    # 'custom.dataloader',
    # 'custom.actions',
)

os.environ.setdefault('RELATIVE_SETTINGS_MODULE', '')
RELATIVE_SETTINGS_MODULE = os.environ.get('RELATIVE_SETTINGS_MODULE')

for app in CUSTOM_APPS:
    try:
        app_settings = import_module(
            f"{app}.settings{RELATIVE_SETTINGS_MODULE}", ["settings"])

        for setting in dir(app_settings):
            if setting == setting.upper():
                globals()[setting] = getattr(app_settings, setting)

    except ImportError:
        pass

INSTALLED_APPS += CUSTOM_APPS

JWT_AUTH['JWT_EXPIRATION_DELTA'] = timedelta(hours=1)
JWT_AUTH['JWT_AUTH_COOKIE'] = 'jwt'

STATIC_ROOT = '/code/public/static/'
STATIC_URL = '/static_dj/'
MEDIA_ROOT = '/code/public/media/'

TERRA_APPLIANCE_SETTINGS = {
    'approbation_statuses': {
        'REFUSED': -1,
        'PENDING': 0,
        'WAITING_FOR_INFORMATION': 1,
        'ACCEPTED': 2,
    },
    'REMIND_DELTA_DAYS': 2,
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST', 'db'),
        'PORT': '',
    }
}

SERIALIZATION_MODULES = {
    'geojson': 'terracommon.terra.serializers.geojson',
}

# Make django configurable via environment
SETTINGS_ENV_PREFIX = 'DJANGO__'
# Those settings will throw a launch failure in deploy envs
# if they are not explicitly set
EXPLICIT_ENV_VARS = ['SECRET_KEY']
ENV_VARS = EXPLICIT_ENV_VARS + [
    'EMAIL_HOST',
    'EMAIL_PORT',
    'EMAIL_USE_TLS',
    'EMAIL_HOST_USER',
    'EMAIL_HOST_PASSWORD',
    'DEFAULT_FROM_EMAIL']
DJANGO_ENV_VARS = {}

# Scan environ for django configuration items
for i, val in os.environ.items():
    # Bring back prefixed env vars
    # eg DJANGO__SECRET_KEY to SECRET_KEY form.
    if i.startswith(SETTINGS_ENV_PREFIX):
        s = prefix.join(i.split(SETTINGS_ENV_PREFIX)[1:])
        DJANGO_ENV_VARS[s] = val
    #
    # Look also at the environ Root for explicit env vars
    #  Please note that prefixed value will always have
    #  the higher priority (DJANGO__FOO vs FOO)
    for s in ENV_VARS:
        if s not in DJANGO_ENV_VARS:
            try:
                DJANGO_ENV_VARS[s] = os.environ[s]
            except KeyError:
                pass

# export back DJANGO_ENV_VARS dict as django settings
for s, val in DJANGO_ENV_VARS.items():
    globals()[s] = val


def as_bool(value, asbool=True):
    if isinstance(string, six.string_types):
        if value and asbool:
            low = value.lower().strip()
            if low in [
                'non', 'no', 'n', 'off', '0', '',
            ]:
                return False
            if low in [
                'oui', 'yes', 'y', 'on', '1',
            ]:
                return True
    return bool(value)


def check_explicit_settings(g=None):
    if g is None:
        g = globals()
    for i in EXPLICIT_ENV_VARS:
        try:
            _ = g[i]  #noqa
        except KeyError:
            raise Error('{0} django settings is not defined')


def set_prod_settings(g, env):
    check_explicit_settings(g)
    g.setdefault('EMAIL_HOST', 'localhost')
    g.setdefault('EMAIL_PORT', 1025)
    g.setdefault('EMAIL_USE_TLS', False)
    g.setdefault('DEFAULT_FROM_EMAIL', f'{env}-{{cookiecutter.lname}}@{{cookiecutter.tld_domain}}')
    g['CORS_ORIGIN_WHITELIST '] = (
        f'{env}-terralego-{{cookiecutter.lname}}.{{cookiecutter.tld_domain}}',  #noqa
    )
    g['ALLOWED_HOSTS'] = [
        f'{env}-terralego-{{cookiecutter.lname}}.{{cookiecutter.tld_domain}}',
        '.{{cookiecutter.tld_domain}}'
    ]
    return g
