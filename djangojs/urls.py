# -*- coding: utf-8 -*-
import sys

from os.path import join, isdir

from django.conf.urls import patterns, url

from djangojs.conf import settings
from djangojs.views import UrlsJsonView, ContextJsonView, JsInitView

js_info_dict = {
    'packages': [],
}

for app in settings.INSTALLED_APPS:
    module = sys.modules[app]
    for path in module.__path__:
        if isdir(join(path, 'locale')):
            js_info_dict['packages'].append(app)

urlpatterns = patterns('',
    url(r'^init\.js$', JsInitView.as_view(), name='django_js_init'),
    url(r'^urls$', UrlsJsonView.as_view(), name='django_js_urls'),
    url(r'^context$', ContextJsonView.as_view(), name='django_js_context'),
    url(r'^translation$', 'django.views.i18n.javascript_catalog', js_info_dict, name='js_catalog'),
)
