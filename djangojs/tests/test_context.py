import json

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings
from django.conf import global_settings
from django.utils import translation

from djangojs.conf import settings
from djangojs.utils import ContextSerializer


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
class ContextAsJsonTest(ContextTestMixin, TestCase):

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
