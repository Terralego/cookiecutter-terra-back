# -*- coding: utf-8 -*-
"""
Django settings

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""
from __future__ import absolute_import, division, print_function

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

###############################################################################
# Environment settings routines, compliant with 12Factor: https://12factor.net/
#  The settings are loaded (first has more priority):
#  - maybe from: .instances.<env>
#  - maybe from: .local
#  - one of: .{prod, dev, test}
#  - environ: Most of the base variables can be redefined
#    via environment variables
#  - this file: .base
###############################################################################

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
for cenvvar, value in os.environ.items():
    # Bring back prefixed env vars
    # eg DJANGO__SECRET_KEY to SECRET_KEY form.
    if cenvvar.startswith(SETTINGS_ENV_PREFIX):
        setting = SETTINGS_ENV_PREFIX.join(
            cenvvar.split(SETTINGS_ENV_PREFIX)[1:])
        DJANGO_ENV_VARS[setting] = value
    #
    # Look also at the environ Root for explicit env vars
    #  Please note that prefixed value will always have
    #  the higher priority (DJANGO__FOO vs FOO)
    for setting in ENV_VARS:
        if setting not in DJANGO_ENV_VARS:
            try:
                DJANGO_ENV_VARS[setting] = os.environ[setting]
            except KeyError:
                pass

# export back DJANGO_ENV_VARS dict as django settings
globs = globals()
for setting, value in six.iteritems(DJANGO_ENV_VARS):
    globs[setting] = value


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


def locals_settings_update(_locals, mapping=None):
    '''
    Update _locals dict with mapping dict filtering module special variables.
    mapping: any dict, and potentially a globals/locals __dict__

    return:
        _locals: updated with mapping vars/vals
        __name__ if any: most of the cases, it's use to determine the environment (name)
    '''
    if mapping is None:
        mapping = {}
    for var, value in six.iteritems(mapping):
        if var in [
            '__name__', '__doc__', '__package__',
            '__loader__', '__spec__', '__file__',
            '__cached__', '__builtins__'
        ]:
            continue
        _locals[var] = value
    return _locals, mapping.get('__name__', '').split('.')[-1]


def filter_globals():
    '''
    Shortcut helper to locals_settings_update() to only get
    the filtered globals from this current module without special variables
    '''
    return locals_settings_update({}, globals())[0]


def check_explicit_settings(_locals):
    '''
    verify that some vars are explicitly defined
    '''
    for setting in EXPLICIT_ENV_VARS:
        try:
            _ = _locals[setting]  #noqa
        except KeyError:
            raise Exception('{0} django settings is not defined')


def post_process_settings(globs=None):
    '''
    Make intermediary processing on settings like:
        - checking explicit vars
        - tranforming vars which can come from system environment as strings
          in their final values as django settings
    '''
    _locals, env = locals_settings_update(locals(), globs)
    check_explicit_settings(_locals)
    for setting, func, fkwargs in (
        ('EMAIL_PORT', as_int, {}),
        ('EMAIL_USE_TLS', as_bool, {}),
        ('CORS_ORIGIN_ALLOW_ALL', as_bool, {}),
        ('CORS_ORIGIN_WHITELIST', as_col, {'final_type': tuple}),
        ('ALLOWED_HOSTS', as_col, {}),
    ):
        try:
            _locals[setting]
        except KeyError:
            continue
        _locals[setting] = func(_locals[setting], **fkwargs)
    {% if cookiecutter.with_sentry -%}SENTRY_DSN = _locals.setdefault('SENTRY_DSN', '')
    SENTRY_RELEASE = _locals.setdefault('SENTRY_RELEASE', 'prod')
    INSTALLED_APPS = _locals.setdefault('INSTALLED_APPS', tuple())
    SENTRY_TAGS = _locals.pop('SENTRY_TAGS', None)
    if SENTRY_DSN:
        if 'raven.contrib.django.raven_compat' not in INSTALLED_APPS:
            # type is used to handle both INSTALLED_APPS setted as a tuple or a list
            _locals['INSTALLED_APPS'] = (
                type(
                    _locals['INSTALLED_APPS']
                )(['raven.contrib.django.raven_compat']) +
                _locals['INSTALLED_APPS'])
        RAVEN_CONFIG = _locals.setdefault('RAVEN_CONFIG', {})
        RAVEN_CONFIG.setdefault('release', SENTRY_RELEASE)
        RAVEN_CONFIG['dsn'] = SENTRY_DSN
        RAVEN_CONFIG.setdefault(
            'transport',
            'raven.transport.requests.RequestsHTTPTransport')
        # If you are using git, you can also automatically
        # configure the release based on the git info.
        LOGGING = _locals.setdefault('LOGGING', copy.deepcopy(DEFAULT_LOGGING))
        LOGGING['disable_existing_loggers'] = True
        LOGGING.setdefault('handlers', {}).update({
            'sentry': {
                'level': 'ERROR',
                'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',  #noqa
            }})
        root = LOGGING.setdefault('root', {})
        root['handlers'] = ['sentry']
        if SENTRY_TAGS and isinstance(SENTRY_TAGS, six.string_types):
            _locals['SENTRY_TAGS'] = {}
            for tagentry in SENTRY_TAGS.split(','):
                tag = tagentry.split(':')[0]
                value = ':'.join(tagentry.split(':')[1:])
                if not value:
                    value = tag
                    tag = 'general'
                _locals['SENTRY_TAGS'][tag] = value
        if 'DEPLOY_ENV' in _locals:
            _locals['RAVEN_CONFIG']['environment'] = _locals['DEPLOY_ENV']
    {%- endif %}
    globals().update(_locals)
    return _locals, filter_globals(), env


def set_prod_settings(globs):
    '''
    Additional post processing of settings only ran on hosted environments
    '''
    _locals, env = locals_settings_update(locals(), globs)
    SERVER_EMAIL = _locals.setdefault(
        'SERVER_EMAIL',
        '{env}-{{cookiecutter.lname}}@{{cookiecutter.tld_domain}}'.format(env=env))
    _locals.setdefault('ADMINS', [('root', SERVER_EMAIL)])
    _locals.setdefault('EMAIL_HOST', 'localhost')
    _locals.setdefault('DEFAULT_FROM_EMAIL', SERVER_EMAIL)
    ALLOWED_HOSTS = _locals.setdefault('ALLOWED_HOSTS', [])
    CORS_ORIGIN_WHITELIST = _locals.setdefault(
        'CORS_ORIGIN_WHITELIST', tuple())
    CORS_ORIGIN_REGEX_WHITELIST = _locals.setdefault(
        'CORS_ORIGIN_REGEX_WHITELIST', tuple())
    # those settings by default are empty, we need to handle this case
    if not CORS_ORIGIN_WHITELIST:
        _locals['CORS_ORIGIN_WHITELIST'] = (
            '{env}-terralego-{{cookiecutter.lname}}.{{cookiecutter.tld_domain}}'.format(env=env),  #noqa
            '.{{cookiecutter.tld_domain}}')
    if env in ['dev', 'qa', 'staging']:
        _locals['CORS_ORIGIN_REGEX_WHITELIST'] += ('^(https?://){{cookiecutter.lname}}front.local(:[0-9]+)?($|/)', )
    if not ALLOWED_HOSTS:
        _locals['ALLOWED_HOSTS'] = [
            '{env}-terralego-{{cookiecutter.lname}}.{{cookiecutter.tld_domain}}'.format(env=env),
            '.{{cookiecutter.tld_domain}}']
    globals().update(_locals)
    return _locals, filter_globals(), env
