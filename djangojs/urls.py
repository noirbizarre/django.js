# -*- coding: utf-8 -*-
import sys

from os.path import join, isdir

from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from djangojs.conf import settings
from djangojs.views import DjangoJsJsonView, TestFormView, JasmineRunner

js_info_dict = {
    'packages': [],
}

for app in settings.INSTALLED_APPS:
    module = sys.modules[app]
    for path in module.__path__:
        if isdir(join(path, 'locale')):
            js_info_dict['packages'].append(app)

urlpatterns = patterns('',
    url(r'^urls$', DjangoJsJsonView.as_view(), name='django_js_json'),
    url(r'^trans$', 'django.views.i18n.javascript_catalog', js_info_dict, name='js_catalog'),
)

if settings.DEBUG or settings.TESTING:
    urlpatterns += patterns('',
        url(r'^tests/jasmine$', JasmineRunner.as_view(), name='jasmine_runner'),
        url(r'^tests/form$', TestFormView.as_view(), name='test_form'),
        url(r'^tests/arg/(\d+)$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name='test_arg'),
        url(r'^tests/arg/(\d+)/(\w)$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name='test_arg_multi'),
        url(r'^tests/named/(?P<test>\w+)$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name='test_named'),
        url(r'^tests/named/(?P<str>\w+)/(?P<num>\d+)$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name='test_named_multi'),
        url(r'^tests/optionnals?$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name="opt"),
        url(r'^tests/many?/optionnals?$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name="opt_multi"),
        url(r'^tests/optionnal/(?:capturing)?group$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name="opt_grp"),
        url(r'^tests/anonymous$', TemplateView.as_view(template_name='djangojs/test/test1.html')),
    )
