# -*- coding: utf-8 -*-
import sys

from os.path import join, isdir

from django.conf.urls import patterns, url, include

from djangojs.conf import settings
from djangojs.views import DjangoJsJsonView

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
        url(r'^tests/', include('djangojs.test_urls')),
    )
