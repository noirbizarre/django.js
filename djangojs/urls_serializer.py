# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
import re
import sys
import types

from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import RegexURLPattern, RegexURLResolver
from django.utils import six

from djangojs.conf import settings

logger = logging.getLogger(__name__)


__all__ = (
    'urls_as_dict',
    'urls_as_json',
)

RE_KWARG = re.compile(r"(\(\?P\<(.*?)\>.*?\))")  # Pattern for recongnizing named parameters in urls
RE_ARG = re.compile(r"(\(.*?\))")  # Pattern for recognizing unnamed url parameters
RE_OPT = re.compile(r"(?:\w|/)(?:\?|\*)")  # Pattern for recognizing optionnal character
RE_OPT_GRP = re.compile(r"\(\?\:.*\)(?:\?|\*)")  # Pattern for recognizing optionnal group
RE_ESCAPE = re.compile(r'([^\\]?)\\')  # Recognize escape characters
RE_START_END = re.compile(r'[\$\^]')  # Recognize start and end charaters

try:  # check for django-cms
    from cms.appresolver import AppRegexURLResolver
    CMS_APP_RESOLVER = True
except:
    CMS_APP_RESOLVER = False  # we can live without it


def urls_as_dict():
    '''
    Get the URLs mapping as a dictionnary
    '''
    module = settings.ROOT_URLCONF
    return _get_urls(module) if settings.JS_URLS_ENABLED else {}


def urls_as_json():
    '''
    Get the URLs mapping as JSON
    '''
    return json.dumps(urls_as_dict(), cls=DjangoJSONEncoder)


def _get_urls_for_pattern(pattern, prefix='', namespace=None):
    urls = {}

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
                return {}
            if settings.JS_URLS_EXCLUDE and pattern_name in settings.JS_URLS_EXCLUDE:
                return {}
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
    elif (CMS_APP_RESOLVER) and (issubclass(pattern.__class__, AppRegexURLResolver)):  # hack for django-cms
        for p in pattern.url_patterns:
            urls.update(_get_urls_for_pattern(p, prefix=prefix, namespace=namespace))
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


def _get_urls(module, prefix='', namespace=None):
    urls = {}
    if isinstance(module, (six.text_type, six.string_types)):
        try:
            __import__(module)
            root_urls = sys.modules[module]
            patterns = root_urls.urlpatterns
        except ImportError:  # die silently
            patterns = tuple()
    elif isinstance(module, (list, tuple)):
        patterns = module
    elif isinstance(module, types.ModuleType):
        patterns = module.urlpatterns
    else:
        raise TypeError('Unsupported type: %s' % type(module))

    for pattern in patterns:
        urls.update(_get_urls_for_pattern(pattern, prefix=prefix, namespace=namespace))

    return urls
