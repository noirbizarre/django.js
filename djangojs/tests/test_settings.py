from django.test import TestCase
from django.test.utils import override_settings


@override_settings(USE_I18N=True, LANGUAGE_CODE='en', JS_I18N_APPS=['djangojs'])
class I18nIncludeTest(TestCase):
    def setUp(self):
        from djangojs.urls import js_info_dict
        self.packages = js_info_dict()['packages']

    def test_include_translation(self):
        '''Should include apps listed in JS_I18N'''
        self.assertTrue('djangojs' in self.packages)

    def test_not_include_translation(self):
        '''Should not include apps not listed in JS_I18N'''
        self.assertFalse('djangojs.fake' in self.packages)


@override_settings(USE_I18N=True, LANGUAGE_CODE='en', JS_I18N_APPS_EXCLUDE=['djangojs'])
class I18nExcludeTest(TestCase):
    def setUp(self):
        from djangojs.urls import js_info_dict
        self.packages = js_info_dict()['packages']

    def test_include_translation(self):
        '''Should exclude apps listed in JS_I18N_EXCLUDE'''
        self.assertFalse('djangojs' in self.packages)

    def test_not_include_translation(self):
        '''Should not exlude apps not listed in JS_I18N_EXCLUDE'''
        self.assertTrue('djangojs.fake' in self.packages)
