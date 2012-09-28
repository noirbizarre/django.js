from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from djangojs.views import DjangoJsJsonView


urlpatterns = patterns('',
    url(r'^urls$', DjangoJsJsonView.as_view(), name='django_js_json'),
    url(r'^1st/(\d+)$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name='first_test'),
    url(r'^2nd/(?P<test>\w+)$', TemplateView.as_view(template_name='djangojs/test/test1.html'), name='second_test'),
    url(r'^tests?$', TemplateView.as_view(template_name='djangojs/test/specrunner.html'), name='test_runner'),
)
