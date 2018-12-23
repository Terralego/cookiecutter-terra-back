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


def as_col(value, separators=None, final_type=None, **kw):
    if final_type is None:
        final_type = list
    if separators is None:
        separators = ['-|_', '_|-', '___', ',', ';', '|']
    if isinstance(value, six.string_types):
        assert(len(separators))
        while separators:
            try:
                separator = separators.pop(0)
            except IndexError:
                break
            if separator in value:
                break
        value = final_type(value.split(separator))
        if final_type is not list:
            value = final_type(value)
    return value


def as_int(value, **kw):
    if value not in ['', None]:
        value = int(value)
    return value


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


def locals_settings_update(locals_, d=None):
    if d is None:
        d = {}
    for a, b in six.iteritems(d):
        if a in [
            '__name__', '__doc__', '__package__',
            '__loader__', '__spec__', '__file__',
            '__cached__', '__builtins__'
        ]:
            continue
        locals_[a] = b
    return locals_, d.get('__name__', '').split('.')[-1]


def module_settings_update(mod, locals_):
    if mod is not None:
        mod.__dict__.update(locals_)
    return locals_


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
exec('import {0} as BASESETTINGSMODULE'.format(__name__))
for s, val in DJANGO_ENV_VARS.items():
    setattr(BASESETTINGSMODULE, s, val)


def check_explicit_settings(outerns=None):
    '''
    verify that some vars are explicitly defined
    '''
    locals_, env = locals_settings_update(locals(), outerns.__dict__)
    for i in EXPLICIT_ENV_VARS:
        try:
            _ = locals_[i]  #noqa
        except KeyError:
            raise Error('{0} django settings is not defined')
    return module_settings_update(outerns, locals_), outerns, env


def post_process_settings(outerns=None):
    '''
    Make intermediary processing on settings like:
        - checking explicit vars
        - tranforming vars which can come from system environment as strings
          in their final values as django settings
    '''
    locals_, outerns, env = check_explicit_settings(outerns)
    for setting, func, fkw in (
        ('EMAIL_PORT', as_int, {}),
        ('EMAIL_USE_TLS', as_bool, {}),
        ('CORS_ORIGIN_ALLOW_ALL', as_bool, {}),
        ('CORS_ORIGIN_WHITELIST', as_col, {'final_type': tuple}),
        ('ALLOWED_HOSTS', as_col, {}),
    ):
        try:
            locals_[setting]
        except KeyError:
            continue
        locals_[setting] = func(locals_[setting], **fkw)
    {% if cookiecutter.with_sentry -%}SENTRY_DSN = locals_.setdefault('SENTRY_DSN', '')
    SENTRY_RELEASE = locals_.setdefault('SENTRY_RELEASE', 'prod')
    if SENTRY_DSN:
        if 'raven.contrib.django.raven_compat' not in INSTALLED_APPS:
            INSTALLED_APPS = (
                type(INSTALLED_APPS)(['raven.contrib.django.raven_compat']) +
                INSTALLED_APPS)
        RAVEN_CONFIG = locals_.setdefault('RAVEN_CONFIG', {})
        RAVEN_CONFIG['dsn'] = SENTRY_DSN
        RAVEN_CONFIG.setdefault('transport',
                     'raven.transport.requests.RequestsHTTPTransport')
        RAVEN_CONFIG.setdefault('release', SENTRY_RELEASE)
    {%- endif %}
    return module_settings_update(outerns, locals_), outerns, env


def set_prod_settings(outerns=None):
    '''
    Additional post processing of settings only ran on hosted environments
    '''
    locals_, env = locals_settings_update(locals(), outerns.__dict__)
    {% if cookiecutter.with_sentry -%}SENTRY_DSN = locals_.setdefault('SENTRY_DSN', '')
    if SENTRY_DSN:
        # If you are using git, you can also automatically
        # configure the release based on the git info.
        log = locals_.setdefault('LOGGING', copy.deepcopy(DEFAULT_LOGGING))
        RAVEN_CONFIG = locals_.setdefault('RAVEN_CONFIG', {})
        root = log.setdefault('root', {})
        root['handlers'] = ['sentry']
        log['disable_existing_loggers'] = True
        log.setdefault('handlers', {}).update({
            'sentry': {
                'level': 'ERROR',
                'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',  #noqa
            }})
        if 'DEPLOY_ENV' in locals_:
            locals_['RAVEN_CONFIG']['environment'] = locals_['DEPLOY_ENV']
    {%- endif %}
    SERVER_EMAIL = locals_.setdefault(
        'SERVER_EMAIL',
        '{env}-{{cookiecutter.lname}}@{{cookiecutter.tld_domain}}'.format(env=env))
    ADMINS = [('root', SERVER_EMAIL)]
    EMAIL_HOST = locals_.setdefault('EMAIL_HOST', 'localhost')
    DEFAULT_FROM_EMAIL = locals_.setdefault('DEFAULT_FROM_EMAIL', SERVER_EMAIL)
    ALLOWED_HOSTS = locals_.setdefault('ALLOWED_HOSTS', [])
    CORS_ORIGIN_WHITELIST = locals_.setdefault(
        'CORS_ORIGIN_WHITELIST', tuple())
    # those settings by default are empty, we need to handle this case
    if not CORS_ORIGIN_WHITELIST:
        CORS_ORIGIN_WHITELIST = (
            '{env}-terralego-{{cookiecutter.lname}}.{{cookiecutter.tld_domain}}'.format(env=env),  #noqa
            '.{{cookiecutter.tld_domain}}')
    if not ALLOWED_HOSTS:
        ALLOWED_HOSTS = [
            '{env}-terralego-{{cookiecutter.lname}}.{{cookiecutter.tld_domain}}'.format(env=env),
            '.{{cookiecutter.tld_domain}}']
    return module_settings_update(outerns, locals_), outerns, env
