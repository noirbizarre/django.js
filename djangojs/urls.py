# -*- coding: utf-8 -*-
import sys

from os.path import join, isdir

from django.conf.urls import patterns, url

from djangojs.conf import settings
from djangojs.views import DjangoJsJsonView
from djangojs.views import JasmineView, QUnitView

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
        url(r'^jasmine$', JasmineView.as_view(), name='default_jasmine_runner'),
        url(r'^qunit$', QUnitView.as_view(), name='default_qunit_runner'),
    )
