import json

from django.core.urlresolvers import reverse
from django.template import Context, Template
from django.test import TestCase

from djangojs.conf import settings
from djangojs.runners import JsTestCase
from djangojs.views import JsTestView


class JsTests(JsTestCase):
    urls = 'djangojs.test_urls'

    def test_jasmine_suite(self):
        '''It should run its its own Jasmine test suite'''
        self.run_jasmine('djangojs_jasmine', title='Jasmine Test Suite')

    def test_qunit_suite(self):
        '''It should run its its own QUnit test suite'''
        self.run_qunit('djangojs_qunit', title='QUnit Test Suite')


class DjangoJsJsonTest(TestCase):
    urls = 'djangojs.test_urls'

    def setUp(self):
        self.response = self.client.get(reverse('django_js_json'))
        self.json = json.loads(self.response.content)

    def test_render(self):
        '''It should render a JSON URLs descriptor'''
        self.assertIsNotNone(self.response)
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response['Content-Type'], 'application/json')
        self.assertIsNotNone(self.json)

    def test_simple_url(self):
        '''It should serialize a simple URL without parameters'''
        self.assertTrue('django_js_json' in self.json)
        self.assertEqual(self.json['django_js_json'], '/djangojs/urls')

    def test_url_an_arg(self):
        '''It should serialize an URL with a single anonymous parameter'''
        self.assertTrue('test_arg' in self.json)
        self.assertEqual(self.json['test_arg'], '/test/arg/<>')

    def test_url_many_args(self):
        '''It should serialize an URL with many anonymous parameters'''
        self.assertTrue('test_arg_multi' in self.json)
        self.assertEqual(self.json['test_arg_multi'], '/test/arg/<>/<>')

    def test_url_a_kwarg(self):
        '''It should serialize an URL with a single named parameter'''
        self.assertTrue('test_named' in self.json)
        self.assertEqual(self.json['test_named'], '/test/named/<test>')

    def test_url_many_kwargs(self):
        '''It should serialize an URL with many named parameters'''
        self.assertTrue('test_named_multi' in self.json)
        self.assertEqual(self.json['test_named_multi'], '/test/named/<str>/<num>')

    def test_unnamed_url(self):
        '''It should not serialize unnamed URLs'''
        self.assertFalse('' in self.json)
        for key, value in self.json.iteritems():
            self.assertNotEqual(value, '/test/anonymous')

    def test_optionnal_chars(self):
        '''It should not serialize optionnal characters (take the shortest)'''
        self.assertTrue('opt' in self.json)
        url = self.json['opt']
        self.assertFalse('?' in url)
        self.assertEqual(url, '/test/optionnal')

        self.assertTrue('opt_multi' in self.json)
        url = self.json['opt_multi']
        self.assertFalse('?' in url)
        self.assertEqual(url, '/test/man/optionnal')

    def test_optionnal_groups(self):
        '''It should not serialize optionnal non capturing groups'''
        self.assertTrue('opt_grp' in self.json)
        url = self.json['opt_grp']
        self.assertFalse('?' in url)
        self.assertEqual(url, '/test/optionnal/group')


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
        self.failUnless('<script type="text/javascript" src="%sjs/libs/jquery-1.8.2.min.js">' % settings.STATIC_URL in rendered)

    def test_django_js(self):
        '''Should include and initialize django.js'''
        t = Template('''
            {% load js %}
            {% django_js %}
            ''')
        rendered = t.render(Context())
        self.failUnless('<script type="text/javascript" src="%sjs/libs/jquery-1.8.2.min.js">' % settings.STATIC_URL in rendered)
        self.failUnless('<script type="text/javascript" src="%sjs/djangojs/django.js">' % settings.STATIC_URL in rendered)
        self.failUnless('window.DJANGO_INFOS' in rendered)
        self.failUnless('Django.init();' in rendered)

    def test_django_js_init_false(self):
        '''Should include and not initialize django.js'''
        t = Template('''
            {% load js %}
            {% django_js init=false %}
            ''')
        rendered = t.render(Context())
        self.failUnless('<script type="text/javascript" src="%sjs/libs/jquery-1.8.2.min.js">' % settings.STATIC_URL in rendered)
        self.failUnless('<script type="text/javascript" src="%sjs/djangojs/django.js">' % settings.STATIC_URL in rendered)
        self.failUnless('window.DJANGO_INFOS' in rendered)
        self.failIf('Django.init();' in rendered)

    def test_django_js_jquery_false(self):
        '''Should include django.js without jQuery'''
        t = Template('''
            {% load js %}
            {% django_js jquery=false %}
            ''')
        rendered = t.render(Context())
        self.failIf('<script type="text/javascript" src="%sjs/libs/jquery-1.8.2.min.js">' % settings.STATIC_URL in rendered)
        self.failUnless('<script type="text/javascript" src="%sjs/djangojs/django.js">' % settings.STATIC_URL in rendered)

    def test_django_js_init_jquery_false(self):
        '''Should include unintialized initialize django.js without jQuery'''
        t = Template('''
            {% load js %}
            {% django_js init=false jquery=false %}
            ''')
        rendered = t.render(Context())
        self.failIf('<script type="text/javascript" src="%sjs/libs/jquery-1.8.2.min.js">' % settings.STATIC_URL in rendered)
        self.failUnless('<script type="text/javascript" src="%sjs/djangojs/django.js">' % settings.STATIC_URL in rendered)
        self.failUnless('window.DJANGO_INFOS' in rendered)
        self.failIf('Django.init();' in rendered)

    def test_django_js_i18n(self):
        '''Should include django.js with i18n support'''
        t = Template('''
            {% load js %}
            {% django_js %}
            ''')
        rendered = t.render(Context())
        self.failUnless('<script type="text/javascript" src="%sjs/libs/jquery-1.8.2.min.js">' % settings.STATIC_URL in rendered)
        self.failUnless('<script type="text/javascript" src="%sjs/djangojs/django.js">' % settings.STATIC_URL in rendered)
        self.failUnless('<script type="text/javascript" src="/trans">' in rendered)
        self.failUnless('window.DJANGO_INFOS' in rendered)


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
