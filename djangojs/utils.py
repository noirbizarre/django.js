# -*- coding: utf-8 -*-
'''
This modules holds every helpers that does not fit in any standard django modules.

It might be splitted in futur releases.
'''
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
from django.utils import translation

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
RE_OPT = re.compile(r"\w\?")  # Pattern for recognizing optionnal character
RE_OPT_GRP = re.compile(r"\(\?\:.*\)\?")  # Pattern for recognizing optionnal group


def urls_as_dict():
    '''
    Get the URLs mapping as a dictionnary
    '''
    if not hasattr(settings, 'ROOT_URLCONF'):
        raise Exception
    module = settings.ROOT_URLCONF
    return _get_urls(module)


def urls_as_json():
    '''
    Get the URLs mapping as JSON
    '''
    return json.dumps(urls_as_dict(), cls=DjangoJSONEncoder)


def _get_urls(module, prefix='', namespace=None):
    urls = {}
    if isinstance(module, (str, unicode)):
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
            if pattern.name:
                pattern_name = pattern.name
                if settings.JS_URLS and pattern_name not in settings.JS_URLS:
                    continue
                if settings.JS_URLS_EXCLUDE and pattern_name in settings.JS_URLS_EXCLUDE:
                    continue
                if namespace:
                    pattern_name = ':'.join((namespace, pattern_name))
                full_url = prefix + pattern.regex.pattern
                for chr in ['^', '$']:
                    full_url = full_url.replace(chr, '')
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
                urls[pattern_name] = "/" + full_url
        elif issubclass(pattern.__class__, RegexURLResolver):
            if pattern.urlconf_name:
                # Add urls twice: for app and instance namespace
                for ns in set((pattern.namespace, pattern.app_name)):
                    namespaces = filter(None, (namespace, ns))
                    namespaces = ':'.join(namespaces)
                    if settings.JS_URLS_NAMESPACES and namespaces and namespaces not in settings.JS_URLS_NAMESPACES:
                        continue
                    if settings.JS_URLS_NAMESPACES_EXCLUDE and namespaces in settings.JS_URLS_NAMESPACES_EXCLUDE:
                        continue
                    new_prefix = '%s%s' % (prefix, pattern.regex.pattern)
                    urls.update(_get_urls(pattern.urlconf_name, new_prefix, namespaces))
    return urls


class ContextSerializer(object):
    '''
    Serialize the context from requests.
    '''
    SERIALIZERS = {
        'LANGUAGES': 'serialize_languages',
        # 'perms': 'serialize_perms',
    }

    @classmethod
    def as_dict(cls, request):
        '''
        Serialize the context as a dictionnary from a given request.
        '''
        data = {}
        for context in RequestContext(request):
            for key, value in context.iteritems():
                # print key, value
                if key in cls.SERIALIZERS:
                    serializer_name = cls.SERIALIZERS[key]
                    if hasattr(cls, serializer_name):
                        serializer = getattr(cls, serializer_name)
                        data[key] = serializer(value)
                elif isinstance(value, (str, tuple, list, dict, int, bool, set)):
                    data[key] = value
        if 'LANGUAGE_CODE' in data:
            # Dirty hack to fix non included default
            language_code = 'en' if data['LANGUAGE_CODE'] == 'en-us' else data['LANGUAGE_CODE']
            language = translation.get_language_info(language_code)
            data['LANGUAGE_NAME'] = language['name']
            data['LANGUAGE_NAME_LOCAL'] = language['name_local']
        return data

    @classmethod
    def as_json(cls, request):
        '''
        Serialize the context as JSON from a given request.
        '''
        return json.dumps(cls.as_dict(request), cls=DjangoJSONEncoder)

    @classmethod
    def serialize_perms(cls, perms):
        print perms
        return None

    @classmethod
    def serialize_languages(cls, languages):
        return dict(languages)


class StorageGlobber(object):
    '''
    Retrieve file list from static file storages.
    '''
    @classmethod
    def glob(cls, files=[]):
        '''
        Glob a pattern or a list of pattern static storage relative(s).
        '''
        if isinstance(files, str):
            matches = lambda path: matches_patterns(path, [files])
        elif isinstance(files, (list, tuple)):
            matches = lambda path: matches_patterns(path, files)
        return [path for path in cls.get_static_files() if matches(path)]

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
