# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from djangojs.views import TestFormView, JasmineRunner

urlpatterns = patterns('',
    url(r'^jasmine$', JasmineRunner.as_view(), name='jasmine_runner'),
    url(r'^form$', TestFormView.as_view(), name='test_form'),
    url(r'^arg/(\d+)$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name='test_arg'),
    url(r'^arg/(\d+)/(\w)$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name='test_arg_multi'),
    url(r'^named/(?P<test>\w+)$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name='test_named'),
    url(r'^named/(?P<str>\w+)/(?P<num>\d+)$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name='test_named_multi'),
    url(r'^optionnals?$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name="opt"),
    url(r'^many?/optionnals?$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name="opt_multi"),
    url(r'^optionnal/(?:capturing)?group$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name="opt_grp"),
    url(r'^anonymous$', TemplateView.as_view(template_name='djangojs/test/test1.html')),
)
