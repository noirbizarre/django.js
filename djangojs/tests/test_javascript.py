from django.conf import global_settings
from django.test.utils import override_settings
from django.utils.translation import ugettext_lazy as _

from djangojs.runners import JsTestCase, JsTemplateTestCase, JasmineSuite, QUnitSuite


@override_settings(
    TEMPLATE_CONTEXT_PROCESSORS=global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
        'djangojs.tests.custom_processor',
    ),
    LANGUAGES=(
        ('en-us', _('English')),
        ('fr', _('French')),
    )
)
class DjangoJsTests(JasmineSuite, JsTestCase):
    urls = 'djangojs.test_urls'
    url_name = 'djangojs_tests'


class JasmineTests(JasmineSuite, JsTestCase):
    urls = 'djangojs.test_urls'
    url_name = 'djangojs_jasmine_tests'


class JasmineTemplateTests(JasmineSuite, JsTemplateTestCase):
    js_files = 'js/test/jasmine/*Spec.js'


class QUnitTests(QUnitSuite, JsTestCase):
    urls = 'djangojs.test_urls'
    url_name = 'djangojs_qunit_tests'


class QUnitTemplateTests(QUnitSuite, JsTemplateTestCase):
    template_name = 'djangojs/test/qunit-test-runner.html'
    js_files = 'js/test/qunit/qunit-*.js'
