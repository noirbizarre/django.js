from django.test import TestCase
from django.test.utils import override_settings
from djangojs.urls import js_info_dict


@override_settings(USE_I18N=True, LANGUAGE_CODE='en',
                   INSTALLED_APPS=['djangojs', 'djangojs.fake'],
                   JS_I18N_APPS=['djangojs'])
class I18nIncludeTest(TestCase):
    def setUp(self):
        self.packages = js_info_dict()['packages']

    def test_include_translation(self):
        '''Should include apps listed in JS_I18N'''
        self.assertIn('djangojs', self.packages)

    def test_not_include_translation(self):
        '''Should not include apps not listed in JS_I18N'''
        self.assertNotIn('djangojs.fake', self.packages)


@override_settings(USE_I18N=True, LANGUAGE_CODE='en',
                   INSTALLED_APPS=['djangojs', 'djangojs.fake'],
                   JS_I18N_APPS_EXCLUDE=['djangojs'])
class I18nExcludeTest(TestCase):
    def setUp(self):
        self.packages = js_info_dict()['packages']

    def test_exclude_translation(self):
        '''Should exclude apps listed in JS_I18N_EXCLUDE'''
        self.assertNotIn('djangojs', self.packages)

    def test_not_exclude_translation(self):
        '''Should not exlude apps not listed in JS_I18N_EXCLUDE'''
        self.assertIn('djangojs.fake', self.packages)
