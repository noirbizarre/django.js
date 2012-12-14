from django.core.urlresolvers import reverse
from django.template import Context, Template
from django.test import TestCase

from djangojs import JQUERY_VERSION
from djangojs.conf import settings


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
