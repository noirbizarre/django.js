import sys

from os.path import join, isdir

from django.conf import settings
from django.conf.urls import patterns, url
from django.views.generic import TemplateView

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
    url(r'^1st/(\d+)$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name='first_test'),
    url(r'^2nd/(?P<test>\w+)$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name='second_test'),
    url(r'^tests?$', TemplateView.as_view(template_name='djangojs/test/specrunner.html'), name='test_runner'),

)
