import json

from django.conf import global_settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django.utils import translation

from djangojs.conf import settings
from djangojs.utils import ContextSerializer


class FakeModel(models.Model):
    something = models.CharField(max_length=256)

    class Meta:
        app_label = 'fake'
        permissions = (
            ("do_smething", "Can do something"),
            ("do_something_else", "Can do something else"),
        )


class ContextTestMixin(object):

    def setUp(self):
        self.factory = RequestFactory()

    def process_request(self, admin=False):
        request = self.factory.get(reverse('django_js_context'))
        if admin:
            request.user = User.objects.create_superuser('admin', 'fake@noirbizarre.info', 'password')
        else:
            request.user = User.objects.create_user('user', 'fake@noirbizarre.info', 'password')
        return self.get_result(request)

    def test_static_url(self):
        '''STATIC_URL should be in context'''
        result = self.process_request()
        self.assertIn('STATIC_URL', result)
        self.assertEqual(result['STATIC_URL'], settings.STATIC_URL)

    def test_media_url(self):
        '''MEDIA_URL should be in context'''
        result = self.process_request()
        self.assertIn('MEDIA_URL', result)
        self.assertEqual(result['MEDIA_URL'], settings.MEDIA_URL)

    def test_language_code(self):
        '''LANGUAGE_CODE should be in context'''
        result = self.process_request()
        self.assertIn('LANGUAGE_CODE', result)
        self.assertEqual(result['LANGUAGE_CODE'], translation.get_language())

    def test_language_bidi(self):
        '''LANGUAGE_BIDI should be in context'''
        result = self.process_request()
        self.assertIn('LANGUAGE_BIDI', result)
        self.assertEqual(result['LANGUAGE_BIDI'], translation.get_language_bidi())

    def test_language_name(self):
        '''LANGUAGE_NAME should be in context'''
        result = self.process_request()
        self.assertIn('LANGUAGE_NAME', result)
        code = translation.get_language()
        code = 'en' if code == 'en-us' else code
        language = translation.get_language_info(code)
        self.assertEqual(result['LANGUAGE_NAME'], language['name'])

    def test_language_name_local(self):
        '''LANGUAGE_NAME_LOCAL should be in context'''
        result = self.process_request()
        self.assertTrue('LANGUAGE_NAME_LOCAL' in result)
        code = translation.get_language()
        code = 'en' if code == 'en-us' else code
        language = translation.get_language_info(code)
        self.assertEqual(result['LANGUAGE_NAME_LOCAL'], language['name_local'])

    def test_languages(self):
        '''LANGUAGE_BIDI should be in context'''
        result = self.process_request()
        self.assertIn('LANGUAGES', result)
        languages = result['LANGUAGES']
        self.assertTrue(isinstance(languages, dict))
        for code, name in settings.LANGUAGES:
            self.assertEqual(languages[code], name)

    def test_any_custom_context_processor(self):
        '''Any custom context processor should be in context'''
        result = self.process_request()
        self.assertIn('CUSTOM', result)
        self.assertEqual(result['CUSTOM'], 'CUSTOM_VALUE')

    def test_user(self):
        '''Basic user informations should be in context'''
        result = self.process_request()
        self.assertIn('user', result)
        self.assertIn('username', result['user'])
        self.assertEqual(result['user']['username'], 'user')
        self.assertIn('is_authenticated', result['user'])
        self.assertTrue(result['user']['is_authenticated'])
        self.assertIn('is_staff', result['user'])
        self.assertFalse(result['user']['is_staff'])
        self.assertIn('is_superuser', result['user'])
        self.assertFalse(result['user']['is_superuser'])
        self.assertIn('permissions', result['user'])
        self.assertTrue(isinstance(result['user']['permissions'], (list, tuple)))

    def test_super_user(self):
        '''Basic superuser informations should be in context'''
        result = self.process_request(True)

        self.assertEqual(result['user']['username'], 'admin')
        self.assertTrue(result['user']['is_authenticated'])
        self.assertTrue(result['user']['is_staff'])
        self.assertTrue(result['user']['is_superuser'])

    def test_user_permissions(self):
        '''Should list permissions'''
        result = self.process_request(True)
        self.assertIn('permissions', result['user'])
        self.assertTrue(isinstance(result['user']['permissions'], (list, tuple)))
        # Default permissions
        for perm in ('add', 'change', 'delete'):
            self.assertIn('fake.%s_fakemodel' % perm, result['user']['permissions'])
        # Custom permissions
        for perm in ('do_smething', 'do_something_else'):
            self.assertIn('fake.%s' % perm, result['user']['permissions'])

    def test_user_without_permissions(self):
        '''Should not list denied permissions'''
        result = self.process_request()
        self.assertIn('permissions', result['user'])
        self.assertTrue(isinstance(result['user']['permissions'], (list, tuple)))
        self.assertEqual(len(result['user']['permissions']), 0)


@override_settings(
    TEMPLATE_CONTEXT_PROCESSORS=global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
        'djangojs.tests.custom_processor',
    )
)
class ContextAsDictTest(ContextTestMixin, TestCase):

    def get_result(self, request):
        return ContextSerializer.as_dict(request)


@override_settings(
    TEMPLATE_CONTEXT_PROCESSORS=global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
        'djangojs.tests.custom_processor',
    )
)
class ContextAsJsonTest(ContextTestMixin, TestCase):

    def get_result(self, request):
        return json.loads(ContextSerializer.as_json(request))


@override_settings(
    TEMPLATE_CONTEXT_PROCESSORS=global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
        'djangojs.tests.custom_processor',
    )
)
class ContextJsonViewTest(TestCase):
    urls = 'djangojs.test_urls'

    def test_render(self):
        '''It should render a JSON Context descriptor'''
        response = self.client.get(reverse('django_js_context'))

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertIsNotNone(json.loads(response.content.decode()))
