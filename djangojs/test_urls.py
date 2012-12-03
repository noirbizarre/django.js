# -*- coding: utf-8 -*-
from django import forms
from django.conf.urls import patterns, url, include
from django.core.urlresolvers import reverse
from django.views.generic.edit import BaseFormView
from django.views.generic import TemplateView

from djangojs.views import JasmineView, QUnitView


class TestForm(forms.Form):
    message = forms.CharField()


class TestFormView(BaseFormView):
    form_class = TestForm

    def get_success_url(self):
        return reverse('opt')


class DjangoJsTestView(JasmineView):
    template_name = 'djangojs/test/djangojs-test-runner.html'
    js_files = 'test/js/specs/django.specs.js'
    django_js = True

    def get_context_data(self, **kwargs):
        context = super(DjangoJsTestView, self).get_context_data(**kwargs)
        context['form'] = TestForm()
        return context


class JasmineTestView(JasmineView):
    js_files = 'test/js/specs/jasmine/*Spec.js'


class QUnitTestView(QUnitView):
    template_name = 'djangojs/test/qunit-test-runner.html'
    js_files = 'test/js/tests/qunit-*.js'


urlpatterns = patterns('',
    url(r'^djangojs/', include('djangojs.urls')),

    url(r'^tests$', DjangoJsTestView.as_view(), name='djangojs_tests'),
    url(r'^jasmine$', JasmineTestView.as_view(), name='djangojs_jasmine_tests'),
    url(r'^qunit$', QUnitTestView.as_view(), name='djangojs_qunit_tests'),


    url(r'^test/form$', TestFormView.as_view(), name='test_form'),
    url(r'^test/arg/(\d+)$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name='test_arg'),
    url(r'^test/arg/(\d+)/(\w)$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name='test_arg_multi'),
    url(r'^test/named/(?P<test>\w+)$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name='test_named'),
    url(r'^test/named/(?P<str>\w+)/(?P<num>\d+)$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name='test_named_multi'),
    url(r'^test/optionnals?$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name="opt"),
    url(r'^test/many?/optionnals?$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name="opt_multi"),
    url(r'^test/optionnal/(?:capturing)?group$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name="opt_grp"),
)
