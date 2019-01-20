# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from ..prod import *

locs_, globs_, env = set_prod_settings(locals())
globals().update(globs_)
# Already set in ansible code, only here for example
# hosts = ['0.0.0.0', 'www.mixity.co', 'mixity.co',]
# CORS_ORIGIN_WHITELIST = CORS_ORIGIN_WHITELIST + tuple(hosts)
# ALLOWED_HOSTS.extend(hosts)
SWAGGER_ENABLED = True
# vim:set et sts=4 ts=4 tw=80:
