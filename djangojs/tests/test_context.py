# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils import unittest
import json

from django.conf import global_settings
from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import User
from django.contrib.contenttypes.management import update_contenttypes
from django.core.urlresolvers import reverse
from django.db.models import get_app
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django.utils import translation
from django.middleware.locale import LocaleMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django import VERSION as DJANGO_VERSION

from djangojs.conf import settings
from djangojs.utils import ContextSerializer

TEST_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'djangojs.tests.custom_processor',
    'django.core.context_processors.i18n',
)

TEST_MIDDLEWARES = global_settings.MIDDLEWARE_CLASSES + (
    'django.middleware.locale.LocaleMiddleware',
)


class ContextTestMixin(object):

    def setUp(self):
        self.factory = RequestFactory()

    def process_request(self, admin=False, headers=None, custom=False):
        headers = headers if headers else {}
        request = self.factory.get(reverse('django_js_context'), **headers)
        SessionMiddleware().process_request(request)
        LocaleMiddleware().process_request(request)
        if admin:
            request.user = User.objects.create_superuser('admin', 'fake@noirbizarre.info', 'password')
        elif custom:
            from djangojs.fake.models import CustomUser
            request.user = CustomUser(identifier='custom')
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

    @override_settings(LANGUAGE_CODE='en-us')
    def test_language_code(self):
        '''LANGUAGE_CODE should be in context'''
        result = self.process_request(headers={'HTTP_ACCEPT_LANGUAGE': 'fr'})
        self.assertIn('LANGUAGE_CODE', result)
        self.assertEqual(result['LANGUAGE_CODE'], 'fr')

    @override_settings(LANGUAGE_CODE='en-us')
    def test_language_code_default(self):
        '''Should handle the default LANGUAGE_CODE="en-us"'''
        result = self.process_request()
        self.assertIn('LANGUAGE_CODE', result)
        self.assertEqual(result['LANGUAGE_CODE'], 'en-us')

    def test_language_bidi(self):
        '''LANGUAGE_BIDI should be in context'''
        result = self.process_request()
        self.assertIn('LANGUAGE_BIDI', result)
        self.assertEqual(result['LANGUAGE_BIDI'], translation.get_language_bidi())

    @override_settings(LANGUAGE_CODE='en-us')
    def test_language_name(self):
        '''LANGUAGE_NAME should be in context'''
        result = self.process_request(headers={'HTTP_ACCEPT_LANGUAGE': 'fr'})
        self.assertIn('LANGUAGE_NAME', result)
        self.assertEqual(result['LANGUAGE_NAME'], 'French')

    @override_settings(LANGUAGE_CODE='en-us')
    def test_language_name_en_us(self):
        '''LANGUAGE_NAME should handle en-us special case'''
        result = self.process_request()
        self.assertIn('LANGUAGE_NAME', result)
        # code = translation.get_language()
        # code = 'en' if code == 'en-us' else code
        # language = translation.get_language_info(code)
        self.assertEqual(result['LANGUAGE_NAME'], 'English')

    def test_language_name_local(self):
        '''LANGUAGE_NAME_LOCAL should be in context'''
        result = self.process_request()
        self.assertIn('LANGUAGE_NAME_LOCAL', result)
        code = translation.get_language()
        code = 'en' if code == 'en-us' else code
        language = translation.get_language_info(code)
        self.assertEqual(result['LANGUAGE_NAME_LOCAL'], language['name_local'])

    @override_settings(DEBUG=True, LANGUAGE_CODE=global_settings.LANGUAGE_CODE)
    def test_language_debug(self):
        '''LANGUAGE_* should be present even in debug with default language'''
        result = self.process_request()
        self.assertIn('LANGUAGE_BIDI', result)
        self.assertIn('LANGUAGE_CODE', result)
        self.assertIn('LANGUAGE_NAME', result)
        self.assertIn('LANGUAGE_NAME_LOCAL', result)

    @override_settings(LANGUAGE_CODE='en-us')
    def test_languages(self):
        '''LANGUAGES should be in context'''
        result = self.process_request()
        self.assertIn('LANGUAGES', result)
        languages = result['LANGUAGES']
        self.assertTrue(isinstance(languages, dict))
        for code, name in settings.LANGUAGES:
            self.assertEqual(languages[code], name)

    @override_settings(LANGUAGE_CODE='en-us')
    def test_languages_localized(self):
        '''LANGUAGES should be localized'''
        result = self.process_request(headers={'HTTP_ACCEPT_LANGUAGE': 'fr'})
        self.assertIn('LANGUAGES', result)
        languages = result['LANGUAGES']
        self.assertTrue(isinstance(languages, dict))
        translation.activate('fr')
        for code, name in settings.LANGUAGES:
            self.assertEqual(languages[code], translation.ugettext_lazy(name))

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
        self.fake_permissions()
        result = self.process_request(True)

        self.assertIn('permissions', result['user'])
        self.assertTrue(isinstance(result['user']['permissions'], (list, tuple)))

        # Default permissions
        for perm in ('add', 'change', 'delete'):
            self.assertIn('fake.%s_fakemodel' % perm, result['user']['permissions'])
        # Custom permissions
        for perm in ('do_something', 'do_something_else'):
            self.assertIn('fake.%s' % perm, result['user']['permissions'])

    def test_user_without_permissions(self):
        '''Should not list denied permissions'''
        result = self.process_request()
        self.assertIn('permissions', result['user'])
        self.assertTrue(isinstance(result['user']['permissions'], (list, tuple)))
        self.assertEqual(len(result['user']['permissions']), 0)

    @unittest.skipIf(DJANGO_VERSION < (1, 5), "Custom user model exists only in Django 1.5+")
    @override_settings(AUTH_USER_MODEL='fake.CustomUser')
    def test_custom_user_model(self):
        '''Should have at least degraded informations on custom user model in Django 1.5+'''
        result = self.process_request(custom=True)
        self.assertIn('user', result)
        self.assertIn('username', result['user'])
        self.assertEqual(result['user']['username'], 'custom')
        self.assertIn('is_authenticated', result['user'])
        self.assertTrue(result['user']['is_authenticated'])
        self.assertIn('is_staff', result['user'])
        self.assertFalse(result['user']['is_staff'])
        self.assertIn('is_superuser', result['user'])
        self.assertFalse(result['user']['is_superuser'])
        self.assertIn('permissions', result['user'])
        self.assertTrue(isinstance(result['user']['permissions'], (list, tuple)))

    def fake_permissions(self):
        ''' Add fake app missing content types and permissions'''
        app = get_app('fake')
        update_contenttypes(app, None, 0)
        create_permissions(app, None, 0)


@override_settings(
    TEMPLATE_CONTEXT_PROCESSORS=TEST_CONTEXT_PROCESSORS,
    MIDDLEWARE_CLASSES=TEST_MIDDLEWARES,
    INSTALLED_APPS=['djangojs', 'djangojs.fake']
)
class ContextAsDictTest(ContextTestMixin, TestCase):

    def get_result(self, request):
        return ContextSerializer.as_dict(request)


@override_settings(
    TEMPLATE_CONTEXT_PROCESSORS=TEST_CONTEXT_PROCESSORS,
    MIDDLEWARE_CLASSES=TEST_MIDDLEWARES,
    INSTALLED_APPS=['djangojs', 'djangojs.fake']
)
class ContextAsJsonTest(ContextTestMixin, TestCase):

    def get_result(self, request):
        return json.loads(ContextSerializer.as_json(request))


@override_settings(
    TEMPLATE_CONTEXT_PROCESSORS=TEST_CONTEXT_PROCESSORS,
    MIDDLEWARE_CLASSES=TEST_MIDDLEWARES,
    INSTALLED_APPS=['djangojs', 'djangojs.fake']
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
