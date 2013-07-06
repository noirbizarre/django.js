# -*- coding: utf-8 -*-
from django import forms
from django.conf.urls import patterns, url, include
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import BaseFormView

from djangojs.views import JasmineView, QUnitView


def unnamed(request, **kwargs):
    return None


class TestForm(forms.Form):
    message = forms.CharField()


class TestFormView(BaseFormView):
    form_class = TestForm

    def get_success_url(self):
        return reverse('opt')


class DjangoJsTestView(JasmineView):
    template_name = 'djangojs/test/djangojs-test-runner.html'
    js_files = 'js/test/django.specs.js'
    django_js = True

    def get_context_data(self, **kwargs):
        context = super(DjangoJsTestView, self).get_context_data(**kwargs)
        context['form'] = TestForm()
        return context


class JasmineTestView(JasmineView):
    js_files = 'js/test/jasmine/*Spec.js'


class QUnitTestView(QUnitView):
    template_name = 'djangojs/test/qunit-test-runner.html'
    js_files = 'js/test/qunit/qunit-*.js'


fake_patterns = patterns('',
    url(r'^fake$', TestFormView.as_view(), name='fake'),
)

nested_patterns = patterns('',
    url(r'^nested/', include(fake_patterns, namespace="nested", app_name="appnested")),
)

other_fake_patterns = patterns('',
    url(r'^fake$', TestFormView.as_view(), name='fake'),
)

test_patterns = patterns('',
    url(r'^form$', TestFormView.as_view(), name='test_form'),
    url(r'^unamed$', 'djangojs.test_urls.unnamed'),
    url(r'^unnamed-class$', TestFormView.as_view()),
    url(r'^arg/(\d+)$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name='test_arg'),
    url(r'^arg/(\d+)/(\w)$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name='test_arg_multi'),
    url(r'^named/(?P<test>\w+)$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name='test_named'),
    url(r'^named/(?P<str>\w+)/(?P<num>\d+)$',
        TemplateView.as_view(template_name='djangojs/test/test1.html'),
        name='test_named_multi'),
    url(r'^named/(?P<test>\d+(?:,\d+)*)$',
        TemplateView.as_view(template_name='djangojs/test/test1.html'),
        name='test_named_nested'),
    url(r'^optionnals?$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name="opt"),
    url(r'^optionnal/?$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name="opt-trailing-slash"),
    url(r'^many?/optionnals?$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name="opt_multi"),
    url(r'^optionnal/(?:capturing)?group$',
        TemplateView.as_view(template_name='djangojs/test/test1.html'),
        name="opt_grp"),
    url(r'^first/$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name='twice'),
    url(r'^last/$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name='twice'),
    url(r'^namespace1/', include(fake_patterns, namespace="ns1", app_name="app1")),
    url(r'^namespace2/', include(nested_patterns, namespace="ns2", app_name="app2")),
    url(r'^namespace3/', include(fake_patterns, namespace="ns3")),
    url(r'^test\.json$', TestFormView.as_view(), name='escaped'),
)

urlpatterns = patterns('',
    url(r'^$', DjangoJsTestView.as_view(), name='djangojs_tests'),

    url(r'^djangojs/', include('djangojs.urls')),

    url(r'^jasmine/$', JasmineTestView.as_view(), name='djangojs_jasmine_tests'),
    url(r'^qunit/$', QUnitTestView.as_view(), name='djangojs_qunit_tests'),

    url(r'^test/', include(test_patterns)),
)
