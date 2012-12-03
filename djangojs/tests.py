import json
import unittest

from django.core.urlresolvers import reverse
from django.template import Context, Template
from django.test import TestCase
from django.test.utils import override_settings
from django.conf import global_settings
from django.utils import translation

from djangojs import JQUERY_VERSION
from djangojs.conf import settings
from djangojs.runners import JsTestCase, JasmineMixin, QUnitMixin
from djangojs.tap import TapParser, TapTest, TapModule, TapAssertion
from djangojs.utils import urls_as_dict, urls_as_json, ContextSerializer
from djangojs.views import JsTestView


def custom_processor(request):
    return {'CUSTOM': 'CUSTOM_VALUE'}


@override_settings(
    TEMPLATE_CONTEXT_PROCESSORS=global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
        'djangojs.tests.custom_processor',
    )
)
class DjangoJsTests(JasmineMixin, JsTestCase):
    urls = 'djangojs.test_urls'
    runner_url_name = 'djangojs_tests'


class JasmineTests(JasmineMixin, JsTestCase):
    urls = 'djangojs.test_urls'
    runner_url_name = 'djangojs_jasmine_tests'


class QUnitTests(QUnitMixin, JsTestCase):
    urls = 'djangojs.test_urls'
    runner_url_name = 'djangojs_qunit_tests'


class UrlsTestMixin(object):
    urls = 'djangojs.test_urls'

    def test_simple_url(self):
        '''It should serialize a simple URL without parameters'''
        self.assertTrue('django_js_urls' in self.result)
        self.assertEqual(self.result['django_js_urls'], '/djangojs/urls')

    def test_url_an_arg(self):
        '''It should serialize an URL with a single anonymous parameter'''
        self.assertTrue('test_arg' in self.result)
        self.assertEqual(self.result['test_arg'], '/test/arg/<>')

    def test_url_many_args(self):
        '''It should serialize an URL with many anonymous parameters'''
        self.assertTrue('test_arg_multi' in self.result)
        self.assertEqual(self.result['test_arg_multi'], '/test/arg/<>/<>')

    def test_url_a_kwarg(self):
        '''It should serialize an URL with a single named parameter'''
        self.assertTrue('test_named' in self.result)
        self.assertEqual(self.result['test_named'], '/test/named/<test>')

    def test_url_many_kwargs(self):
        '''It should serialize an URL with many named parameters'''
        self.assertTrue('test_named_multi' in self.result)
        self.assertEqual(self.result['test_named_multi'], '/test/named/<str>/<num>')

    def test_unnamed_url(self):
        '''It should not serialize unnamed URLs'''
        self.assertFalse('' in self.result)
        for key, value in self.result.iteritems():
            self.assertNotEqual(value, '/test/anonymous')

    def test_optionnal_chars(self):
        '''It should not serialize optionnal characters (take the shortest)'''
        self.assertTrue('opt' in self.result)
        url = self.result['opt']
        self.assertFalse('?' in url)
        self.assertEqual(url, '/test/optionnal')

        self.assertTrue('opt_multi' in self.result)
        url = self.result['opt_multi']
        self.assertFalse('?' in url)
        self.assertEqual(url, '/test/man/optionnal')

    def test_optionnal_groups(self):
        '''It should not serialize optionnal non capturing groups'''
        self.assertTrue('opt_grp' in self.result)
        url = self.result['opt_grp']
        self.assertFalse('?' in url)
        self.assertEqual(url, '/test/optionnal/group')


class UrlsAsDictTest(UrlsTestMixin, TestCase):

    def setUp(self):
        self.result = urls_as_dict()


class UrlsAsJsonTest(UrlsTestMixin, TestCase):

    def setUp(self):
        self.result = json.loads(urls_as_json())


class UrlsJsonViewTest(UrlsTestMixin, TestCase):

    def setUp(self):
        self.response = self.client.get(reverse('django_js_urls'))
        self.result = json.loads(self.response.content)

    def test_render(self):
        '''It should render a JSON URLs descriptor'''
        self.assertIsNotNone(self.response)
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response['Content-Type'], 'application/json')
        self.assertIsNotNone(self.result)


class ContextTestMixin(object):

    def test_static_url(self):
        '''STATIC_URL should be in context'''
        self.assertTrue('STATIC_URL' in self.result)
        self.assertEqual(self.result['STATIC_URL'], settings.STATIC_URL)

    def test_media_url(self):
        '''MEDIA_URL should be in context'''
        self.assertTrue('MEDIA_URL' in self.result)
        self.assertEqual(self.result['MEDIA_URL'], settings.MEDIA_URL)

    def test_language_code(self):
        '''LANGUAGE_CODE should be in context'''
        self.assertTrue('LANGUAGE_CODE' in self.result)
        self.assertEqual(self.result['LANGUAGE_CODE'], translation.get_language())

    def test_language_bidi(self):
        '''LANGUAGE_BIDI should be in context'''
        self.assertTrue('LANGUAGE_BIDI' in self.result)
        self.assertEqual(self.result['LANGUAGE_BIDI'], translation.get_language_bidi())

    def test_language_name(self):
        '''LANGUAGE_NAME should be in context'''
        self.assertTrue('LANGUAGE_NAME' in self.result)
        code = translation.get_language()
        code = 'en' if code == 'en-us' else code
        language = translation.get_language_info(code)
        self.assertEqual(self.result['LANGUAGE_NAME'], language['name'])

    def test_language_name_local(self):
        '''LANGUAGE_NAME_LOCAL should be in context'''
        self.assertTrue('LANGUAGE_NAME_LOCAL' in self.result)
        code = translation.get_language()
        code = 'en' if code == 'en-us' else code
        language = translation.get_language_info(code)
        self.assertEqual(self.result['LANGUAGE_NAME_LOCAL'], language['name_local'])

    def test_languages(self):
        '''LANGUAGE_BIDI should be in context'''
        self.assertTrue('LANGUAGES' in self.result)
        languages = self.result['LANGUAGES']
        self.assertTrue(isinstance(languages, dict))
        for code, name in settings.LANGUAGES:
            self.assertEqual(languages[code], name)

    def test_any_custom_context_processor(self):
        '''Any custom context processor should be in context'''
        self.assertTrue('CUSTOM' in self.result)
        self.assertEqual(self.result['CUSTOM'], 'CUSTOM_VALUE')


@override_settings(
    TEMPLATE_CONTEXT_PROCESSORS=global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
        'djangojs.tests.custom_processor',
    )
)
class ContextAsDictTest(ContextTestMixin, TestCase):

    def setUp(self):
        response = self.client.get(reverse('django_js_context'))
        self.result = ContextSerializer.as_dict(response.request)


@override_settings(
    TEMPLATE_CONTEXT_PROCESSORS=global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
        'djangojs.tests.custom_processor',
    )
)
class ContextAsDictTest(ContextTestMixin, TestCase):

    def setUp(self):
        response = self.client.get(reverse('django_js_context'))
        self.result = json.loads(ContextSerializer.as_json(response.request))


@override_settings(
    TEMPLATE_CONTEXT_PROCESSORS=global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
        'djangojs.tests.custom_processor',
    )
)
class ContextJsonViewTest(TestCase):
    urls = 'djangojs.test_urls'

    def setUp(self):
        self.response = self.client.get(reverse('django_js_context'))
        self.result = json.loads(self.response.content)

    def test_render(self):
        '''It should render a JSON Context descriptor'''
        self.assertIsNotNone(self.response)
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response['Content-Type'], 'application/json')
        self.assertIsNotNone(self.result)


class VerbatimTagTest(TestCase):
    def test_rendering(self):
        '''Should escape {{ and }}'''
        t = Template('''
            {% load js %}
            {% verbatim %}
                <p>{{name}}</p>
                {{{rawname}}}
            {% endverbatim %}
            ''')
        rendered = t.render(Context())

        self.failUnless('{{name}}' in rendered)
        self.failUnless('{{{rawname}}}' in rendered)
        # HTML should not be escaped
        self.failUnless('<p>' in rendered)
        self.failUnless('</p>' in rendered)

    def test_rendering_with_tags(self):
        '''Should process django template tags'''
        t = Template('''
            {% load i18n js %}

            {% verbatim %}
                {% trans "with translation" %}
                {{name}}
                <p>{{{rawname}}}</p>
                {# works with comments too #}
            {% endverbatim %}
            ''')
        rendered = t.render(Context())

        self.failUnless('{{name}}' in rendered)
        self.failUnless('{{{rawname}}}' in rendered)
        self.failUnless('with translation' in rendered)
        # Those should not be rendered :
        self.failUnless('{% trans %}' not in rendered)
        self.failUnless('comments' not in rendered)
        # HTML should not be escaped
        self.failUnless('<p>' in rendered)
        self.failUnless('</p>' in rendered)


class DjangoJsTagTest(TestCase):
    urls = 'djangojs.urls'

    def test_js(self):
        '''Should include static js files'''
        t = Template('''
            {% load js %}
            {% js "js/my.js" %}
            ''')
        rendered = t.render(Context())
        self.failUnless('<script type="text/javascript" src="%sjs/my.js">' % settings.STATIC_URL in rendered)

    def test_javascript(self):
        '''Should include static javascript files'''
        t = Template('''
            {% load js %}
            {% javascript "js/my.js" %}
            ''')
        rendered = t.render(Context())
        self.failUnless('<script type="text/javascript" src="%sjs/my.js">' % settings.STATIC_URL in rendered)

    def test_css(self):
        '''Should include static css files'''
        t = Template('''
            {% load js %}
            {% css "css/my.css" %}
            ''')
        rendered = t.render(Context())
        self.failUnless('<link rel="stylesheet" type="text/css" href="%scss/my.css" />' % settings.STATIC_URL in rendered)

    def test_js_lib(self):
        '''Should include js libraries'''
        t = Template('''
            {% load js %}
            {% js_lib "my-lib.js" %}
            ''')
        rendered = t.render(Context())
        self.failUnless('<script type="text/javascript" src="%sjs/libs/my-lib.js">' % settings.STATIC_URL in rendered)

    def test_jquery_js(self):
        '''Should include jQuery library'''
        t = Template('''
            {% load js %}
            {% jquery_js %}
            ''')
        rendered = t.render(Context())
        self.failUnless('<script type="text/javascript" src="%sjs/libs/jquery-%s.min.js">' % (settings.STATIC_URL, JQUERY_VERSION) in rendered)

    def test_django_js(self):
        '''Should include and initialize django.js'''
        t = Template('''
            {% load js %}
            {% django_js %}
            ''')
        rendered = t.render(Context())
        self.failUnless('<script type="text/javascript" src="%sjs/libs/jquery-%s.min.js">' % (settings.STATIC_URL, JQUERY_VERSION) in rendered)
        self.failUnless('<script type="text/javascript" src="%sjs/djangojs/django.js">' % settings.STATIC_URL in rendered)

    def test_django_js_jquery_false(self):
        '''Should include django.js without jQuery'''
        t = Template('''
            {% load js %}
            {% django_js jquery=false %}
            ''')
        rendered = t.render(Context())
        self.failIf('<script type="text/javascript" src="%sjs/libs/jquery-%s.min.js">' % (settings.STATIC_URL, JQUERY_VERSION) in rendered)
        self.failUnless('<script type="text/javascript" src="%sjs/djangojs/django.js">' % settings.STATIC_URL in rendered)

    def test_django_js_crsf_false(self):
        '''Should include django.js without jQuery CRSF patch'''
        t = Template('''
            {% load js %}
            {% django_js crsf=false %}
            ''')
        rendered = t.render(Context())
        self.failUnless('window.DJANGO_JS_CRSF = false;' in rendered)

    def test_django_js_i18n(self):
        '''Should include django.js with i18n support'''
        t = Template('''
            {% load js %}
            {% django_js %}
            ''')
        rendered = t.render(Context())
        self.failUnless('<script type="text/javascript" src="%s">' % reverse('js_catalog') in rendered)

    def test_django_js_i18n_false(self):
        '''Should include django.js without i18n support'''
        t = Template('''
            {% load js %}
            {% django_js i18n=false %}
            ''')
        rendered = t.render(Context())
        self.failIf('<script type="text/javascript" src="%s">' % reverse('js_catalog') in rendered)


class JsTestViewTest(TestCase):

    def test_no_js_file(self):
        view = JsTestView()
        self.assertEqual(view.get_js_files(), [])

    def test_single_js_file(self):
        view = JsTestView(js_files='test/js/libs/jasmine-djangojs.js')
        self.assertEqual(view.get_js_files(), ['test/js/libs/jasmine-djangojs.js'])

    def test_multi_js_file(self):
        view = JsTestView(js_files=['test/js/libs/jasmine-djangojs.js', 'test/js/libs/jasmine.js'])

        files = view.get_js_files()

        self.assertIn('test/js/libs/jasmine-djangojs.js', files)
        self.assertIn('test/js/libs/jasmine.js', files)

    def test_single_glob_expression(self):
        view = JsTestView(js_files='test/js/libs/jasmine-*.js')

        files = view.get_js_files()

        self.assertIn('test/js/libs/jasmine-djangojs.js', files)
        self.assertIn('test/js/libs/jasmine-html.js', files)
        self.assertIn('test/js/libs/jasmine-jquery.js', files)
        self.assertNotIn('test/js/libs/jasmine.js', files)

    def test_multi_glob_expression(self):
        view = JsTestView(js_files=['test/js/libs/jasmine-*.js', 'test/js/libs/qunit-*.js'])

        files = view.get_js_files()

        self.assertIn('test/js/libs/jasmine-djangojs.js', files)
        self.assertIn('test/js/libs/jasmine-html.js', files)
        self.assertIn('test/js/libs/jasmine-jquery.js', files)
        self.assertIn('test/js/libs/qunit-tap.js', files)
        self.assertNotIn('test/js/libs/jasmine.js', files)
        self.assertNotIn('test/js/libs/qunit.js', files)


class TapItemsTest(unittest.TestCase):
    def test_parse_assertion(self):
        pass


class TapParserTest(unittest.TestCase):
    def test_single_test(self):
        '''a single test should output TapAssertion and TapTast'''

        parser = TapParser(TapTest)
        output = '''
# test: should be defined
ok 1
        '''

        for item in parser.parse(output):
            print item.display()
