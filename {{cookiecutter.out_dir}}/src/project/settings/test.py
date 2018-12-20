# -*- coding: utf-8 -*-
import tempfile

from .base import *  # noqa

REST_FRAMEWORK['TEST_REQUEST_DEFAULT_FORMAT'] = 'json'

SECRET_KEY = 'spam-spam-spam-spam'

MEDIA_ROOT = tempfile.mkdtemp()
FILE_UPLOAD_TEMP_DIR = tempfile.mkdtemp()

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Boost perf a little
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

g = post_process_settings(globals())
globals().update(g)
try:
    from .local import *  # noqa
except ImportError:
    pass
