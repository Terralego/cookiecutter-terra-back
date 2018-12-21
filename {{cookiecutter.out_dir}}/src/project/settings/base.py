"""
Django settings

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""
import copy
import os
from datetime import timedelta
from importlib import import_module

import six

from django.utils.log import DEFAULT_LOGGING

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

CORS_ORIGIN_ALLOW_ALL = True

# Mail
EMAIL_HOST = 'mailcatcher'
EMAIL_PORT = 1025

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
        s = SETTINGS_ENV_PREFIX.join(i.split(SETTINGS_ENV_PREFIX)[1:])
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
    if isinstance(value, six.string_types):
        if value and asbool:
            low = value.lower().strip()
            if low in [
                'false', 'non', 'no', 'n', 'off', '0', '',
            ]:
                return False
            if low in [
                'true', 'oui', 'yes', 'y', 'on', '1',
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
    return g


def post_process_settings(g=None):
    if g is None:
        g = globals()
    g = check_explicit_settings(g)
    for setting in (
        'EMAIL_PORT',
    ):
        try:
            if g[setting]:
                g[setting] = int(g[setting])
        except KeyError:
            pass
    for setting in (
        'EMAIL_USE_TLS',
        'CORS_ORIGIN_ALLOW_ALL',
    ):
        try:
            if g[setting]:
                g[setting] = as_bool(g[setting])
        except KeyError:
            pass
    {% if cookiecutter.with_sentry -%}sentry_dsn = g.setdefault('SENTRY_DSN', '')
    if sentry_dsn:
        if 'raven.contrib.django.raven_compat' not in g['INSTALLED_APPS']:
            g['INSTALLED_APPS'] = (
                type(g['INSTALLED_APPS'])(['raven.contrib.django.raven_compat']) +
                g['INSTALLED_APPS'])
    {%- endif %}
    return g


def set_prod_settings(g, env):
    {% if cookiecutter.with_sentry -%}sentry_dsn = g.setdefault('SENTRY_DSN', '')
    sentry_release = g.setdefault('SENTRY_RELEASE', 'prod')
    if sentry_dsn:
        if 'raven.contrib.django.raven_compat' not in g['INSTALLED_APPS']:
            g['INSTALLED_APPS'] = (
                type(g['INSTALLED_APPS'])(['raven.contrib.django.raven_compat']) +
                g['INSTALLED_APPS'])
        s = g.setdefault('RAVEN_CONFIG', {})
        s['dsn'] = sentry_dsn
        s.setdefault('transport',
                     'raven.transport.requests.RequestsHTTPTransport')
        # If you are using git, you can also automatically
        # configure the release based on the git info.
        s.setdefault('release', sentry_release)
        log = g.setdefault('LOGGING', copy.deepcopy(DEFAULT_LOGGING))
        root = log.setdefault('root', {})
        root['handlers'] = ['sentry']
        log['disable_existing_loggers'] = True
        log.setdefault('handlers', {}).update({
            'sentry': {
                'level': 'ERROR',
                'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',  #noqa
                'tags': {},
            }})
        if 'DEPLOY_ENV' in g:
            log['handlers']['sentry']['tags']['deploy_env'] = g['DEPLOY_ENV']
    {%- endif %}
    server_email = g.setdefault(
        'SERVER_EMAIL',
        '{env}-{{cookiecutter.lname}}@{{cookiecutter.tld_domain}}'.format(env=env))
    g.setdefault('admins', [('root', server_email)])
    g.setdefault('EMAIL_HOST', 'localhost')
    g.setdefault('DEFAULT_FROM_EMAIL', server_email)
    g['CORS_ORIGIN_WHITELIST'] = [
        '{env}-terralego-{{cookiecutter.lname}}.{{cookiecutter.tld_domain}}'.format(env=env),  #noqa
        '.{{cookiecutter.tld_domain}}'
    ]
    g['ALLOWED_HOSTS'] = [
        '{env}-terralego-{{cookiecutter.lname}}.{{cookiecutter.tld_domain}}'.format(env=env),
        '.{{cookiecutter.tld_domain}}'
    ]
    return g
