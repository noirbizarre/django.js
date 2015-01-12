# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys

from django.conf import settings as _settings

from djangojs import JQUERY_DEFAULT_VERSION

# Default configuration values for Django.js
# All values used by Django.js needs to appears here.
DEFAULTS = {
    'DEBUG': False,
    'TESTING': 'test' in sys.argv,
    'JS_CONTEXT_ENABLED': True,
    'JS_URLS_ENABLED': True,
    'JS_USER_ENABLED': True,
    'JS_URLS': None,
    'JS_URLS_EXCLUDE': None,
    'JS_URL_CONFS': _settings.ROOT_URLCONF,
    'JS_URLS_NAMESPACES': None,
    'JS_URLS_NAMESPACES_EXCLUDE': None,
    'JS_URLS_UNNAMED': False,
    'JS_CONTEXT': None,
    'JS_CONTEXT_EXCLUDE': None,
    'JS_CONTEXT_PROCESSOR': 'djangojs.context_serializer.ContextSerializer',
    'JS_I18N_APPS': None,
    'JS_I18N_APPS_EXCLUDE': None,
    'JS_I18N_PATTERNS': tuple(),
    'JS_CACHE_DURATION': 24 * 60,
    'JQUERY_VERSION': JQUERY_DEFAULT_VERSION,
}


class DjangoJsSettings(object):
    '''
    Lazy Django settings wrapper for Django.js
    '''
    def __init__(self, wrapped_settings):
        self.wrapped_settings = wrapped_settings

    def __getattr__(self, name):
        if hasattr(self.wrapped_settings, name):
            return getattr(self.wrapped_settings, name)
        elif name in DEFAULTS:
            return DEFAULTS[name]
        else:
            raise AttributeError("'%s' setting not found" % name)

settings = DjangoJsSettings(_settings)
