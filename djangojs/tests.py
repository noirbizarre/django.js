import json
from tempfile import NamedTemporaryFile

from os.path import join, dirname
from subprocess import call

from django.core.urlresolvers import reverse
from django.template import Context, Template
from django.test import LiveServerTestCase, TestCase
from django.test.utils import override_settings


class JsTestCase(LiveServerTestCase):

    def phantomjs(self, *args, **kwargs):
        LINE_SIZE = 70
        separator = '=' * LINE_SIZE
        title = kwargs['title'] if 'title' in kwargs else 'phantomjs output'
        nb_spaces = (LINE_SIZE - len(title)) / 2

        print ''
        print separator
        print ' ' * nb_spaces + title
        print separator

        with NamedTemporaryFile(delete=True) as cookies_file:
            cmd = ('phantomjs', '--cookies-file=%s' % cookies_file.name) + args
            result = call(cmd)

        print separator
        return result


class JasmineTests(JsTestCase):
    urls = 'djangojs.urls'

    def test_jasmine_suite(self):
        '''It should run its its own Jasmine test suite'''
        jasmine_runner_url = ''.join([self.live_server_url, reverse('jasmine_runner')])
        phantomjs_jasmine_runner = join(dirname(__file__), 'phantomjs', 'run-jasmine.js')

        result = self.phantomjs(phantomjs_jasmine_runner, jasmine_runner_url, title='Jasmine test suite')

        self.assertEqual(0, result)


class DjangoJsJsonTest(TestCase):
    urls = 'djangojs.urls'

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
        self.assertEqual(self.json['django_js_json'], '/urls')

    def test_url_an_arg(self):
        '''It should serialize an URL with a single anonymous parameter'''
        self.assertTrue('test_arg' in self.json)
        self.assertEqual(self.json['test_arg'], '/tests/arg/<>')

    def test_url_many_args(self):
        '''It should serialize an URL with many anonymous parameters'''
        self.assertTrue('test_arg_multi' in self.json)
        self.assertEqual(self.json['test_arg_multi'], '/tests/arg/<>/<>')

    def test_url_a_kwarg(self):
        '''It should serialize an URL with a single named parameter'''
        self.assertTrue('test_named' in self.json)
        self.assertEqual(self.json['test_named'], '/tests/named/<test>')

    def test_url_many_kwargs(self):
        '''It should serialize an URL with many named parameters'''
        self.assertTrue('test_named_multi' in self.json)
        self.assertEqual(self.json['test_named_multi'], '/tests/named/<str>/<num>')

    def test_unnamed_url(self):
        '''It should not serialize unnamed URLs'''
        self.assertFalse('' in self.json)
        for key, value in self.json.iteritems():
            self.assertNotEqual(value, '/tests/anonymous')

    def test_optionnal_chars(self):
        '''It should not serialize optionnal characters (take the shortest)'''
        self.assertTrue('opt' in self.json)
        url = self.json['opt']
        self.assertFalse('?' in url)
        self.assertEqual(url, '/tests/optionnal')

        self.assertTrue('opt_multi' in self.json)
        url = self.json['opt_multi']
        self.assertFalse('?' in url)
        self.assertEqual(url, '/tests/man/optionnal')

    def test_optionnal_groups(self):
        '''It should not serialize optionnal non capturing groups'''
        self.assertTrue('opt_grp' in self.json)
        url = self.json['opt_grp']
        self.assertFalse('?' in url)
        self.assertEqual(url, '/tests/optionnal/group')


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

    def test_js_lib(self):
        '''Should include js libraries'''
        t = Template('''
            {% load js %}
            {% js_lib "my-lib.js" %}
            ''')
        rendered = t.render(Context())
        self.failUnless('<script type="text/javascript" src="/static/js/libs/my-lib.js">' in rendered)

    def test_jquery_js(self):
        '''Should include jQuery library'''
        t = Template('''
            {% load js %}
            {% jquery_js %}
            ''')
        rendered = t.render(Context())
        self.failUnless('<script type="text/javascript" src="/static/js/libs/jquery-1.8.2.min.js">' in rendered)

    @override_settings(USE_I18N=False)
    def test_django_js(self):
        '''Should include Django JS'''
        t = Template('''
            {% load js %}
            {% django_js %}
            ''')
        rendered = t.render(Context())
        self.failUnless('<script type="text/javascript" src="/static/js/libs/jquery-1.8.2.min.js">' in rendered)
        self.failUnless('<script type="text/javascript" src="/static/js/djangojs/django.js">' in rendered)
        self.failIf('Django.init(' in rendered)

    @override_settings(USE_I18N=False)
    def test_django_js_init(self):
        '''Should include and initialize Django JS'''
        t = Template('''
            {% load js %}
            {% django_js_init %}
            ''')
        rendered = t.render(Context())
        self.failUnless('<script type="text/javascript" src="/static/js/libs/jquery-1.8.2.min.js">' in rendered)
        self.failUnless('<script type="text/javascript" src="/static/js/djangojs/django.js">' in rendered)
        self.failUnless('Django.init(' in rendered)

    @override_settings(USE_I18N=True)
    def test_django_js_i18n(self):
        '''Should include Django JS with i18n support'''
        t = Template('''
            {% load js %}
            {% django_js %}
            ''')
        rendered = t.render(Context())
        self.failUnless('<script type="text/javascript" src="/static/js/libs/jquery-1.8.2.min.js">' in rendered)
        self.failUnless('<script type="text/javascript" src="/static/js/djangojs/django.js">' in rendered)
        self.failUnless('<script type="text/javascript" src="/trans">' in rendered)
        self.failUnless('window.DJANGO_LANGUAGE_INFO' in rendered)
