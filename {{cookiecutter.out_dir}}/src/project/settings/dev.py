# -*- coding: utf-8 -*-
import logging
import os

from .base import *  # noqa

os.environ['RELATIVE_SETTINGS_MODULE'] = '.dev'
SECRET_KEY = os.environ.get('SECRET_KEY', 'secretkey-superhot-12345678')
ALLOWED_HOSTS = ['*']
DEBUG = True

g = post_process_settings(globals())
globals().update(g)
try:
    from .local import *  # noqa
except ImportError:
    pass
