import json

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings

from djangojs.utils import urls_as_dict, urls_as_json


class UrlsTestMixin(object):
    urls = 'djangojs.test_urls'

    def setUp(self):
        self.result = self.get_result()

    def test_simple_url(self):
        '''It should serialize a simple URL without parameters'''
        self.assertIn('django_js_urls', self.result)
        self.assertEqual(self.result['django_js_urls'], '/djangojs/urls')

    def test_url_an_arg(self):
        '''It should serialize an URL with a single anonymous parameter'''
        self.assertIn('test_arg', self.result)
        self.assertEqual(self.result['test_arg'], '/test/arg/<>')

    def test_url_many_args(self):
        '''It should serialize an URL with many anonymous parameters'''
        self.assertIn('test_arg_multi', self.result)
        self.assertEqual(self.result['test_arg_multi'], '/test/arg/<>/<>')

    def test_url_a_kwarg(self):
        '''It should serialize an URL with a single named parameter'''
        self.assertIn('test_named', self.result)
        self.assertEqual(self.result['test_named'], '/test/named/<test>')

    def test_url_many_kwargs(self):
        '''It should serialize an URL with many named parameters'''
        self.assertIn('test_named_multi', self.result)
        self.assertEqual(self.result['test_named_multi'], '/test/named/<str>/<num>')

    def test_unnamed_url(self):
        '''It should not serialize unnamed URLs'''
        self.assertNotIn('', self.result)
        for value in self.result.itervalues():
            self.assertNotEqual(value, '/test/anonymous')

    def test_optionnal_chars(self):
        '''It should not serialize optionnal characters (take the shortest)'''
        self.assertIn('opt', self.result)
        url = self.result['opt']
        self.assertNotIn('?', url)
        self.assertEqual(url, '/test/optionnal')

        self.assertIn('opt_multi', self.result)
        url = self.result['opt_multi']
        self.assertNotIn('?', url)
        self.assertEqual(url, '/test/man/optionnal')

    def test_optionnal_groups(self):
        '''It should not serialize optionnal non capturing groups'''
        self.assertIn('opt_grp', self.result)
        url = self.result['opt_grp']
        self.assertNotIn('?', url)
        self.assertEqual(url, '/test/optionnal/group')

    def test_keep_priority(self):
        '''It should serialize with priority support'''
        self.assertIn('twice', self.result)
        self.assertEqual(self.result['twice'], reverse('twice'))

    def test_escape(self):
        '''It should unescape escaped characters'''
        self.assertIn('escaped', self.result)
        self.assertEqual(self.result['escaped'], reverse('escaped'))

    def test_single_namespace(self):
        '''It should serialize namespaces'''
        self.assertIn('ns1:fake', self.result)
        self.assertEqual(self.result['ns1:fake'], reverse('ns1:fake'))
        self.assertNotIn('fake', self.result)

    def test_nested_namespaces(self):
        '''It should serialize nested namespaces'''
        self.assertIn('ns2:nested:fake', self.result)
        self.assertEqual(self.result['ns2:nested:fake'], reverse('ns2:nested:fake'))
        self.assertNotIn('nested:fake', self.result)
        self.assertNotIn('ns2:nested', self.result)
        self.assertNotIn('ns2:fake', self.result)
        self.assertNotIn('fake', self.result)
        self.assertNotIn('nested', self.result)

    def test_single_instance_namespace(self):
        '''It should serialize instance namespaces'''
        self.assertIn('app1:fake', self.result)
        self.assertEqual(self.result['app1:fake'], reverse('app1:fake'))

    def test_nested_instance_namespaces(self):
        '''It should serialize nested instance namespaces'''
        self.assertIn('ns2:appnested:fake', self.result)
        self.assertIn('app2:nested:fake', self.result)
        self.assertIn('app2:appnested:fake', self.result)
        self.assertEqual(self.result['ns2:appnested:fake'], reverse('ns2:appnested:fake'))
        self.assertEqual(self.result['app2:nested:fake'], reverse('app2:nested:fake'))
        self.assertEqual(self.result['app2:appnested:fake'], reverse('app2:appnested:fake'))
        self.assertNotIn('appnested:fake', self.result)
        self.assertNotIn('ns2:appnested', self.result)
        self.assertNotIn('app2:fake', self.result)
        self.assertNotIn('fake', self.result)

    def test_single_namespace_without_app_name(self):
        '''It should serialize namespaces without app_name set'''
        self.assertIn('ns3:fake', self.result)
        self.assertEqual(self.result['ns3:fake'], reverse('ns3:fake'))
        self.assertNotIn('fake', self.result)

    @override_settings(JS_URLS=['django_js_urls'])
    def test_urls_whitelist(self):
        '''Should only include urls listed in JS_URLS'''
        self.result = self.get_result()
        self.assertIn('django_js_urls', self.result)
        self.assertNotIn('test_arg', self.result)

    @override_settings(JS_URLS_EXCLUDE=['django_js_urls'])
    def test_urls_blacklist(self):
        '''Should exclude urls listed in JS_URLS_EXCLUDE'''
        self.result = self.get_result()
        self.assertNotIn('django_js_urls', self.result)
        self.assertIn('test_arg', self.result)

    @override_settings(JS_URLS_NAMESPACES=['ns1'])
    def test_urls_namespaces_whitelist(self):
        '''Should only include namespaces listed in JS_URLS_NAMESPACES'''
        self.result = self.get_result()
        self.assertIn('ns1:fake', self.result)
        self.assertNotIn('ns2:nested:fake', self.result)

    @override_settings(JS_URLS_NAMESPACES_EXCLUDE=['ns1'])
    def test_urls_namespaces_blacklist(self):
        '''Should exclude namespaces listed in JS_URLS_NAMESPACES_EXCLUDE'''
        self.result = self.get_result()
        self.assertNotIn('ns1:fake', self.result)
        self.assertIn('ns2:nested:fake', self.result)


class UrlsAsDictTest(UrlsTestMixin, TestCase):

    def get_result(self):
        return urls_as_dict()


class UrlsAsJsonTest(UrlsTestMixin, TestCase):

    def get_result(self):
        return json.loads(urls_as_json())


class UrlsJsonViewTest(UrlsTestMixin, TestCase):

    def get_result(self):
        self.response = self.client.get(reverse('django_js_urls'))
        return json.loads(self.response.content.decode())

    def test_render(self):
        '''It should render a JSON URLs descriptor'''
        self.assertIsNotNone(self.response)
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response['Content-Type'], 'application/json')
        self.assertIsNotNone(self.result)
