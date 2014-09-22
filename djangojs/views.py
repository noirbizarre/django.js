# -*- coding: utf-8 -*-
'''
This module provide helper views for javascript.
'''
from __future__ import unicode_literals

import json
import logging
import re

from django.http import HttpResponse
from django.utils.cache import patch_vary_headers
from django.views.decorators.cache import cache_page
from django.views.generic import View, TemplateView
from django.views.i18n import javascript_catalog

from djangojs.conf import settings
from djangojs.urls_serializer import urls_as_dict, urls_as_json
from djangojs.utils import StorageGlobber, LazyJsonEncoder, class_from_string


logger = logging.getLogger(__name__)


__all__ = (
    'JsInitView',
    'JsonView',
    'UrlsJsonView',
    'ContextJsonView',
    'JsTestView',
    'JasmineView',
    'QUnitView',
)

RE_KWARG = re.compile(r"(\(\?P\<(.*?)\>.*?\))")  # Pattern for recongnizing named parameters in urls
RE_ARG = re.compile(r"(\(.*?\))")  # Pattern for recognizing unnamed url parameters
RE_OPT = re.compile(r"\w\?")  # Pattern for recognizing optionnal character
RE_OPT_GRP = re.compile(r"\(\?\:.*\)\?")  # Pattern for recognizing optionnal group

JSON_MIMETYPE = 'application/json'
JAVASCRIPT_MIMETYPE = 'application/javascript'


class CacheMixin(object):
    '''Apply a JS_CACHE_DURATION to the view'''
    def dispatch(self, *args, **kwargs):
        cache = cache_page(60 * settings.JS_CACHE_DURATION)
        return cache(super(CacheMixin, self).dispatch)(*args, **kwargs)


class UserCacheMixin(CacheMixin):
    def dispatch(self, *args, **kwargs):
        response = super(UserCacheMixin, self).dispatch(*args, **kwargs)
        patch_vary_headers(response, ('Cookie',))
        return response


class JsInitView(UserCacheMixin, TemplateView):
    '''
    Render a javascript file containing the URLs mapping and the context as JSON.
    '''
    template_name = 'djangojs/init.js'

    def get_context_data(self, **kwargs):
        context = super(JsInitView, self).get_context_data(**kwargs)
        context['urls'] = urls_as_json()
        serializer = class_from_string(settings.JS_CONTEXT_PROCESSOR)
        context['context'] = serializer(self.request).as_json()
        return context

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['content_type'] = JAVASCRIPT_MIMETYPE
        return super(JsInitView, self).render_to_response(context, **response_kwargs)


class JsonView(View):
    '''
    A views that render JSON.
    '''
    def get(self, request, **kwargs):
        data = self.get_context_data(**kwargs)
        return HttpResponse(
            json.dumps(data, cls=LazyJsonEncoder),
            content_type=JSON_MIMETYPE
        )


class UrlsJsonView(CacheMixin, JsonView):
    '''
    Render the URLs as a JSON object.
    '''
    def get_context_data(self, **kwargs):
        return urls_as_dict()


class ContextJsonView(UserCacheMixin, JsonView):
    '''
    Render the context as a JSON object.
    '''
    def get_context_data(self, **kwargs):
        serializer = class_from_string(settings.JS_CONTEXT_PROCESSOR)
        return serializer(self.request).as_dict()


class JsTestView(TemplateView):
    '''
    Base class for JS tests views
    '''
    #: A path or a list of path to javascript files to include into the view.
    #:
    #: - Supports glob patterns.
    #: - Order is kept for rendering.
    js_files = None
    #: Includes or not jQuery in the test view.
    jquery = False
    #: Includes or not Django.js in the test view
    django_js = False
    #: Initialize or not Django.js in the test view (only if included)
    django_js_init = True

    def get_context_data(self, **kwargs):
        context = super(JsTestView, self).get_context_data(**kwargs)

        context['js_test_files'] = StorageGlobber.glob(self.js_files)
        context['use_query'] = self.jquery
        context['use_django_js'] = self.django_js
        context['django_js_init'] = self.django_js_init

        return context


class JasmineView(JsTestView):
    '''
    Render a Jasmine test runner.
    '''
    template_name = 'djangojs/jasmine-runner.html'


class QUnitView(JsTestView):
    '''
    Render a QUnit test runner
    '''
    template_name = 'djangojs/qunit-runner.html'

    #: QUnit runner theme.
    #:
    #: Should be one of: qunit, gabe, ninja, nv
    theme = 'qunit'

    def get_context_data(self, **kwargs):
        context = super(QUnitView, self).get_context_data(**kwargs)
        context['css_theme'] = 'js/test/libs/%s.css' % self.theme
        return context


@cache_page(60 * settings.JS_CACHE_DURATION)
def cached_javascript_catalog(request, domain='djangojs', packages=None):
    return javascript_catalog(request, domain, packages)
