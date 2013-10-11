# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging

from django.template.context import RequestContext
from django.utils import translation, six

from djangojs.conf import settings
from djangojs.utils import LazyJsonEncoder

logger = logging.getLogger(__name__)


__all__ = (
    'ContextSerializer',
)

SERIALIZABLE_TYPES = six.string_types + six.integer_types + (six.text_type, tuple, list, dict, bool, set)


class ContextSerializer(object):
    '''
    Serialize context and user from requests.

    Inherits from this class and set your :ref:`settings.JS_CONTEXT_PROCESSOR <js-context-processor>`
    to customize the serialization.

    To add a custom variable serialization handler,
    add a method named ``process_VARNAME(self, value, data)``.
    '''

    def __init__(self, request):
        self.request = request

    def as_dict(self):
        '''
        Serialize the context as a dictionnary from a given request.
        '''
        data = {}
        if settings.JS_CONTEXT_ENABLED:
            for context in RequestContext(self.request):
                for key, value in six.iteritems(context):
                    if settings.JS_CONTEXT and key not in settings.JS_CONTEXT:
                        continue
                    if settings.JS_CONTEXT_EXCLUDE and key in settings.JS_CONTEXT_EXCLUDE:
                        continue
                    handler_name = 'process_%s' % key
                    if hasattr(self, handler_name):
                        handler = getattr(self, handler_name)
                        data[key] = handler(value, data)
                    elif isinstance(value, SERIALIZABLE_TYPES):
                        data[key] = value
        if settings.JS_USER_ENABLED:
            self.handle_user(data)
        return data

    def as_json(self):
        '''
        Serialize the context as JSON.
        '''
        return json.dumps(self.as_dict(), cls=LazyJsonEncoder)

    def process_LANGUAGES(self, languages, data):
        '''Serialize LANGUAGES as a localized dictionnary.'''
        return dict(languages)

    def process_LANGUAGE_CODE(self, language_code, data):
        '''
        Fix language code when set to non included dedfault `en`
        and add the extra variables ``LANGUAGE_NAME`` and ``LANGUAGE_NAME_LOCAL``.
        '''
        # Dirty hack to fix non included default
        language = translation.get_language_info('en' if language_code == 'en-us' else language_code)
        if not settings.JS_CONTEXT or 'LANGUAGE_NAME' in settings.JS_CONTEXT \
            or (settings.JS_CONTEXT_EXCLUDE and 'LANGUAGE_NAME' in settings.JS_CONTEXT_EXCLUDE):
            data['LANGUAGE_NAME'] = language['name']
        if not settings.JS_CONTEXT or 'LANGUAGE_NAME_LOCAL' in settings.JS_CONTEXT \
            or (settings.JS_CONTEXT_EXCLUDE and 'LANGUAGE_NAME_LOCAL' in settings.JS_CONTEXT_EXCLUDE):
            data['LANGUAGE_NAME_LOCAL'] = language['name_local']
        return language_code

    def handle_user(self, data):
        '''
        Insert user informations in data

        Override it to add extra user attributes.
        '''
        # Default to unauthenticated anonymous user
        data['user'] = {
            'username': '',
            'is_authenticated': False,
            'is_staff': False,
            'is_superuser': False,
            'permissions': tuple(),
        }
        if 'django.contrib.sessions.middleware.SessionMiddleware' in settings.MIDDLEWARE_CLASSES:
            user = self.request.user
            data['user']['is_authenticated'] = user.is_authenticated()
            if hasattr(user, 'username'):
                data['user']['username'] = user.username
            elif hasattr(user, 'get_username'):
                data['user']['username'] = user.get_username()
            if hasattr(user, 'is_staff'):
                data['user']['is_staff'] = user.is_staff
            if hasattr(user, 'is_superuser'):
                data['user']['is_superuser'] = user.is_superuser
            if hasattr(user, 'get_all_permissions'):
                data['user']['permissions'] = tuple(user.get_all_permissions())
