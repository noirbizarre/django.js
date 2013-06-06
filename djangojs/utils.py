# -*- coding: utf-8 -*-
'''
This modules holds every helpers that does not fit in any standard django modules.

It might be splitted in futur releases.
'''
from __future__ import unicode_literals

import json
import logging
import os
import re
import sys
import types

from django.contrib.staticfiles import finders
from django.contrib.staticfiles.utils import matches_patterns
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import RegexURLPattern, RegexURLResolver
from django.template.context import RequestContext
from django.utils import translation, six
from django.utils.encoding import force_text
from django.utils.functional import Promise
from django.utils.translation import ugettext_lazy as _

from djangojs.conf import settings

logger = logging.getLogger(__name__)


__all__ = (
    'urls_as_dict',
    'urls_as_json',
    'ContextSerializer',
    'StorageGlobber',
)

RE_KWARG = re.compile(r"(\(\?P\<(.*?)\>.*?\))")  # Pattern for recongnizing named parameters in urls
RE_ARG = re.compile(r"(\(.*?\))")  # Pattern for recognizing unnamed url parameters
RE_OPT = re.compile(r"(?:\w|/)\?")  # Pattern for recognizing optionnal character
RE_OPT_GRP = re.compile(r"\(\?\:.*\)\?")  # Pattern for recognizing optionnal group
RE_ESCAPE = re.compile(r'([^\\]?)\\')  # Recognize escape characters
RE_START_END = re.compile(r'[\$\^]')  # Recognize start and end charaters


def urls_as_dict():
    '''
    Get the URLs mapping as a dictionnary
    '''
    module = settings.ROOT_URLCONF
    return _get_urls(module)


def urls_as_json():
    '''
    Get the URLs mapping as JSON
    '''
    return json.dumps(urls_as_dict(), cls=DjangoJSONEncoder)


def _get_urls(module, prefix='', namespace=None):
    urls = {}
    if isinstance(module, (six.text_type, six.string_types)):
        __import__(module)
        root_urls = sys.modules[module]
        patterns = root_urls.urlpatterns
    elif isinstance(module, (list, tuple)):
        patterns = module
    elif isinstance(module, types.ModuleType):
        patterns = module.urlpatterns
    else:
        raise TypeError('Unsupported type: %s' % type(module))

    for pattern in patterns:
        if issubclass(pattern.__class__, RegexURLPattern):
            if settings.JS_URLS_UNNAMED:
                mod_name, obj_name = pattern.callback.__module__, pattern.callback.__name__
                try:
                    module = __import__(mod_name, fromlist=[obj_name])
                    obj = getattr(module, obj_name)
                    func_name = "{0}.{1}".format(mod_name, obj_name) if isinstance(obj, types.FunctionType) else None
                    pattern_name = pattern.name or func_name
                except:
                    pattern_name = pattern.name
            else:
                pattern_name = pattern.name

            if pattern_name:
                if settings.JS_URLS and pattern_name not in settings.JS_URLS:
                    continue
                if settings.JS_URLS_EXCLUDE and pattern_name in settings.JS_URLS_EXCLUDE:
                    continue
                if namespace:
                    pattern_name = ':'.join((namespace, pattern_name))
                full_url = prefix + pattern.regex.pattern
                for char in ['^', '$']:
                    full_url = full_url.replace(char, '')
                # remove optionnal non capturing groups
                opt_grp_matches = RE_OPT_GRP.findall(full_url)
                if opt_grp_matches:
                    for match in opt_grp_matches:
                        full_url = full_url.replace(match, '')
                # remove optionnal characters
                opt_matches = RE_OPT.findall(full_url)
                if opt_matches:
                    for match in opt_matches:
                        full_url = full_url.replace(match, '')
                # handle kwargs, args
                kwarg_matches = RE_KWARG.findall(full_url)
                if kwarg_matches:
                    for el in kwarg_matches:
                        # prepare the output for JS resolver
                        full_url = full_url.replace(el[0], "<%s>" % el[1])
                # after processing all kwargs try args
                args_matches = RE_ARG.findall(full_url)
                if args_matches:
                    for el in args_matches:
                        full_url = full_url.replace(el, "<>")  # replace by a empty parameter name
                # Unescape charaters
                full_url = RE_ESCAPE.sub(r'\1', full_url)

                urls[pattern_name] = "/" + full_url
        elif issubclass(pattern.__class__, RegexURLResolver):
            if pattern.urlconf_name:
                if pattern.namespace and not pattern.app_name:
                    # Namespace without app_name
                    nss = [pattern.namespace]
                else:
                    # Add urls twice: for app and instance namespace
                    nss = set((pattern.namespace, pattern.app_name))
                for ns in nss:
                    namespaces = [nsp for nsp in (namespace, ns) if nsp]
                    namespaces = ':'.join(namespaces)
                    if settings.JS_URLS_NAMESPACES and namespaces and namespaces not in settings.JS_URLS_NAMESPACES:
                        continue
                    if settings.JS_URLS_NAMESPACES_EXCLUDE and namespaces in settings.JS_URLS_NAMESPACES_EXCLUDE:
                        continue
                    new_prefix = '%s%s' % (prefix, pattern.regex.pattern)
                    urls.update(_get_urls(pattern.urlconf_name, new_prefix, namespaces))
    return urls


class LazyJsonEncoder(DjangoJSONEncoder):
    '''
    A JSON encoder handling promises (aka. Django lazy objects).

    See: https://docs.djangoproject.com/en/dev/topics/serialization/#id2
    '''
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super(LazyJsonEncoder, self).default(obj)


class ContextSerializer(object):
    '''
    Serialize the context from requests.
    '''
    @classmethod
    def as_dict(cls, request):
        '''
        Serialize the context as a dictionnary from a given request.
        '''
        data = {}
        for context in RequestContext(request):
            for key, value in six.iteritems(context):
                processor_name = 'process_%s' % key
                if hasattr(cls, processor_name):
                    processor = getattr(cls, processor_name)
                    data[key] = processor(value, data)
                elif isinstance(value, (str, tuple, list, dict, int, bool, set)):
                    data[key] = value
        cls.handle_user(data, request)
        return data

    @classmethod
    def as_json(cls, request):
        '''
        Serialize the context as JSON from a given request.
        '''
        return json.dumps(cls.as_dict(request), cls=LazyJsonEncoder)

    @classmethod
    def process_LANGUAGES(cls, languages, data):
        return dict((code, _(name)) for code, name in languages)

    @classmethod
    def process_LANGUAGE_CODE(cls, language_code, data):
        # Dirty hack to fix non included default
        language = translation.get_language_info('en' if language_code == 'en-us' else language_code)
        data['LANGUAGE_NAME'] = language['name']
        data['LANGUAGE_NAME_LOCAL'] = language['name_local']
        return language_code

    @classmethod
    def handle_user(cls, data, request):
        '''Insert user informations in data'''
        # Default to unauthenticated anonymous user
        data['user'] = {
            'username': '',
            'is_authenticated': False,
            'is_staff': False,
            'is_superuser': False,
            'permissions': tuple(),
        }
        if 'django.contrib.sessions.middleware.SessionMiddleware' in settings.MIDDLEWARE_CLASSES:
            user = request.user
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


class StorageGlobber(object):
    '''
    Retrieve file list from static file storages.
    '''
    @classmethod
    def glob(cls, files=None):
        '''
        Glob a pattern or a list of pattern static storage relative(s).
        '''
        files = files or []
        if isinstance(files, str):
            matches = lambda path: matches_patterns(path, [files])
            return [path for path in cls.get_static_files() if matches(path)]
        elif isinstance(files, (list, tuple)):
            all_files = cls.get_static_files()
            sorted_result = []
            for pattern in files:
                sorted_result.extend([f for f in all_files if matches_patterns(f, [pattern])])
            return sorted_result

    @classmethod
    def get_static_files(cls):
        files = []
        for finder in finders.get_finders():
            for path, storage in finder.list(None):
                # Prefix the relative path if the source storage contains it
                if getattr(storage, 'prefix', None):
                    prefixed_path = os.path.join(storage.prefix, path)
                else:
                    prefixed_path = path

                if prefixed_path not in files:
                    files.append(prefixed_path)
        return files
