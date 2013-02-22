import unittest

from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.urlresolvers import reverse
from django.template import Context, Template
from django.test import TestCase

from djangojs import JQUERY_DEFAULT_VERSION, JQUERY_MIGRATE_VERSION


@unittest.skipIf(__import__('django').VERSION >= (1, 5), "Django 1.5+ already include a verbatim template tag")
class VerbatimTagTest(TestCase):
    def test_rendering(self):
        '''Should escape {{ and }}'''
        template = Template('''
            {% load js %}
            {% verbatim %}
                <p>{{name}}</p>
                {{{rawname}}}
            {% endverbatim %}
            ''')
        rendered = template.render(Context())

        self.failUnless('{{name}}' in rendered)
        self.failUnless('{{{rawname}}}' in rendered)
        # HTML should not be escaped
        self.failUnless('<p>' in rendered)
        self.failUnless('</p>' in rendered)

    def test_rendering_with_tags(self):
        '''Should process django template tags'''
        template = Template('''
            {% load i18n js %}

            {% verbatim %}
                {% trans "with translation" %}
                {{name}}
                <p>{{{rawname}}}</p>
                {# works with comments too #}
            {% endverbatim %}
            ''')
        rendered = template.render(Context())

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
        template = Template('''
            {% load js %}
            {% js "js/my.js" %}
            ''')
        rendered = template.render(Context())
        self.failUnless('<script type="text/javascript" src="%s">' % static('js/my.js') in rendered)

    def test_javascript(self):
        '''Should include static javascript files'''
        template = Template('''
            {% load js %}
            {% javascript "js/my.js" %}
            ''')
        rendered = template.render(Context())
        self.failUnless('<script type="text/javascript" src="%s">' % static('js/my.js') in rendered)

    def test_css(self):
        '''Should include static css files'''
        template = Template('''
            {% load js %}
            {% css "css/my.css" %}
            ''')
        rendered = template.render(Context())
        self.failUnless('<link rel="stylesheet" type="text/css" href="%s" />' % static('css/my.css') in rendered)

    def test_js_lib(self):
        '''Should include js libraries'''
        template = Template('''
            {% load js %}
            {% js_lib "my-lib.js" %}
            ''')
        rendered = template.render(Context())
        self.failUnless('<script type="text/javascript" src="%s">' % static('js/libs/my-lib.js') in rendered)

    def test_jquery_js(self):
        '''Should include jQuery library'''
        template = Template('''
            {% load js %}
            {% jquery_js %}
            ''')
        rendered = template.render(Context())
        jquery = static('js/libs/jquery-%s.min.js' % JQUERY_DEFAULT_VERSION)
        self.failUnless('<script type="text/javascript" src="%s">' % jquery in rendered)

    def test_jquery_js_version(self):
        '''Should include jQuery library with specified version'''
        template = Template('''
            {% load js %}
            {% jquery_js "1.8.3" %}
            ''')
        rendered = template.render(Context())
        jquery = static('js/libs/jquery-1.8.3.min.js')
        self.failUnless('<script type="text/javascript" src="%s">' % jquery in rendered)

    def test_jquery_js_migrate(self):
        '''Should include jQuery library with migrate'''
        template = Template('''
            {% load js %}
            {% jquery_js migrate="true" %}
            ''')
        rendered = template.render(Context())
        jquery = static('js/libs/jquery-%s.min.js' % JQUERY_DEFAULT_VERSION)
        migrate = static('js/libs/jquery-migrate-%s.min.js' % JQUERY_MIGRATE_VERSION)
        self.failUnless('<script type="text/javascript" src="%s">' % jquery in rendered)
        self.failUnless('<script type="text/javascript" src="%s">' % migrate in rendered)

    def test_django_js(self):
        '''Should include and initialize django.js'''
        template = Template('''
            {% load js %}
            {% django_js %}
            ''')
        rendered = template.render(Context())
        jquery = static('js/libs/jquery-%s.min.js' % JQUERY_DEFAULT_VERSION)
        django_js = static('js/djangojs/django.js')
        self.failUnless('<script type="text/javascript" src="%s">' % jquery in rendered)
        self.failUnless('<script type="text/javascript" src="%s">' % django_js in rendered)

    def test_django_js_jquery_false(self):
        '''Should include django.js without jQuery'''
        template = Template('''
            {% load js %}
            {% django_js jquery="false" %}
            ''')
        jquery = static('js/libs/jquery-%s.min.js' % JQUERY_DEFAULT_VERSION)
        django_js = static('js/djangojs/django.js')

        rendered = template.render(Context())

        self.failIf('<script type="text/javascript" src="%s">' % jquery in rendered)
        self.failUnless('<script type="text/javascript" src="%s">' % django_js in rendered)

    def test_django_js_csrf_false(self):
        '''Should include django.js without jQuery CSRF patch'''
        template = Template('''
            {% load js %}
            {% django_js csrf="false" %}
            ''')
        rendered = template.render(Context())
        self.failUnless('window.DJANGO_JS_CSRF = false;' in rendered)

    def test_django_js_i18n(self):
        '''Should include django.js with i18n support'''
        template = Template('''
            {% load js %}
            {% django_js %}
            ''')
        rendered = template.render(Context())
        self.failUnless('<script type="text/javascript" src="%s">' % reverse('js_catalog') in rendered)

    def test_django_js_i18n_false(self):
        '''Should include django.js without i18n support'''
        template = Template('''
            {% load js %}
            {% django_js i18n="false" %}
            ''')
        rendered = template.render(Context())
        self.failIf('<script type="text/javascript" src="%s">' % reverse('js_catalog') in rendered)
