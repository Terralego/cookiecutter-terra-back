# -*- coding: utf-8 -*-
from .base import *  # noqa

# SECURITY #

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
CORS_ORIGIN_ALLOW_ALL = False
CSRF_COOKIE_HTTPONLY = True
DEBUG = False

# Suppose we are using HTTPS
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = False

STATICFILES_DIRS = []
MEDIA_ACCEL_REDIRECT = False

g = post_process_settings(globals())
globals().update(g)
try:
    from .local import *  # noqa
except ImportError:
    pass
