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

    def test_keep_priority(self):
        '''It should serialize with priority support'''
        self.assertTrue('twice' in self.result)
        self.assertEqual(self.result['twice'], reverse('twice'))

    def test_single_namespace(self):
        '''It should serialize namespaces'''
        self.assertTrue('ns1:fake' in self.result)
        self.assertEqual(self.result['ns1:fake'], reverse('ns1:fake'))
        self.assertFalse('fake' in self.result)

    def test_nested_namespaces(self):
        '''It should serialize nested namespaces'''
        self.assertTrue('ns2:nested:fake' in self.result)
        self.assertEqual(self.result['ns2:nested:fake'], reverse('ns2:nested:fake'))
        self.assertFalse('nested:fake' in self.result)
        self.assertFalse('ns2:nested' in self.result)
        self.assertFalse('ns2:fake' in self.result)
        self.assertFalse('fake' in self.result)
        self.assertFalse('nested' in self.result)

    def test_single_instance_namespace(self):
        '''It should serialize instance namespaces'''
        self.assertTrue('app1:fake' in self.result)
        self.assertEqual(self.result['app1:fake'], reverse('app1:fake'))

    def test_nested_instance_namespaces(self):
        '''It should serialize nested instance namespaces'''
        self.assertTrue('ns2:appnested:fake' in self.result)
        self.assertTrue('app2:nested:fake' in self.result)
        self.assertTrue('app2:appnested:fake' in self.result)
        self.assertEqual(self.result['ns2:appnested:fake'], reverse('ns2:appnested:fake'))
        self.assertEqual(self.result['app2:nested:fake'], reverse('app2:nested:fake'))
        self.assertEqual(self.result['app2:appnested:fake'], reverse('app2:appnested:fake'))
        self.assertFalse('appnested:fake' in self.result)
        self.assertFalse('ns2:appnested' in self.result)
        self.assertFalse('app2:fake' in self.result)

    @override_settings(JS_URLS_NAMESPACES=['ns1'])
    def test_urls_namespaces(self):
        '''Should only include JS_URLS_NAMESPACES'''
        self.result = self.get_result()
        self.assertTrue('ns1:fake' in self.result)
        self.assertFalse('ns2:nested:fake' in self.result)

    @override_settings(JS_URLS_NAMESPACES_EXCLUDE=['ns1'])
    def test_urls_namespaces_exclude(self):
        '''Should only include JS_URLS_NAMESPACES'''
        self.result = self.get_result()
        self.assertFalse('ns1:fake' in self.result)
        self.assertTrue('ns2:nested:fake' in self.result)


class UrlsAsDictTest(UrlsTestMixin, TestCase):

    def get_result(self):
        return urls_as_dict()


class UrlsAsJsonTest(UrlsTestMixin, TestCase):

    def get_result(self):
        return json.loads(urls_as_json())


class UrlsJsonViewTest(UrlsTestMixin, TestCase):

    def get_result(self):
        self.response = self.client.get(reverse('django_js_urls'))
        return json.loads(self.response.content)

    def test_render(self):
        '''It should render a JSON URLs descriptor'''
        self.assertIsNotNone(self.response)
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response['Content-Type'], 'application/json')
        self.assertIsNotNone(self.result)
