# -*- coding: utf-8 -*-
'''
This module provide helper views for javascript.
'''
import json
import logging
import re

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.views.generic import View, TemplateView

from djangojs.utils import urls_as_dict, urls_as_json, ContextSerializer, StorageGlobber

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


class JsInitView(TemplateView):
    '''
    Render a javascript file containing the URLs mapping and the context as JSON.
    '''
    template_name = 'djangojs/init.js'

    def get_context_data(self, **kwargs):
        context = super(JsInitView, self).get_context_data(**kwargs)
        context['urls'] = urls_as_json()
        context['context'] = ContextSerializer.as_json(self.request)
        return context

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['content_type'] = JAVASCRIPT_MIMETYPE
        return super(JsInitView, self).render_to_response(context, **response_kwargs)


class JsonView(View):
    '''
    A views that render JSON.
    '''
    def get(self, request, *args, **kwargs):
        data = self.get_context_data(request, *args, **kwargs)
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
            mimetype=JSON_MIMETYPE
        )


class UrlsJsonView(JsonView):
    '''
    Render the URLs as a JSON object.
    '''
    def get_context_data(self, request, *args, **kwargs):
        return urls_as_dict()


class ContextJsonView(JsonView):
    '''
    Render the context as a JSON object.
    '''
    def get_context_data(self, request, *args, **kwargs):
        return ContextSerializer.as_dict(request)


class JsTestView(TemplateView):
    '''
    Base class for JS tests views
    '''
    #: A path or a list of path to javascript files to include into the view.
    #:
    #: - Supports glob patterns.
    #: - Order is kept for rendering.
    js_files = None
    #: Includes or not Django.js in the test view
    django_js = False
    #: Includes or not jQuery in the test view.
    jquery = False

    def get_context_data(self, **kwargs):
        context = super(JsTestView, self).get_context_data(**kwargs)

        context['js_test_files'] = StorageGlobber.glob(self.js_files)
        context['use_django_js'] = self.django_js
        context['use_query'] = self.jquery

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
