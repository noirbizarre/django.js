from django.test import TestCase

from djangojs.utils import StorageGlobber


class StorageGlobberTest(TestCase):

    def test_no_js_file(self):
        '''Should handle empty js file list'''
        # view = JsTestView()
        self.assertEqual(StorageGlobber.glob(), [])

    def test_single_js_file(self):
        '''Should handle a single js file name as string'''
        files = 'js/test/libs/jasmine-djangojs.js'
        expected = ['js/test/libs/jasmine-djangojs.js']
        self.assertEqual(StorageGlobber.glob(files), expected)

    def test_multi_js_file(self):
        '''Should handle an array of js file names'''
        files = ['js/test/libs/jasmine-djangojs.js', 'js/test/libs/jasmine.js']
        result = StorageGlobber.glob(files)

        self.assertIn('js/test/libs/jasmine-djangojs.js', result)
        self.assertIn('js/test/libs/jasmine.js', result)

    def test_single_glob_expression(self):
        '''Should handle a single glob pattern as js file list'''
        files = 'js/test/libs/jasmine-*.js'
        result = StorageGlobber.glob(files)

        self.assertIn('js/test/libs/jasmine-djangojs.js', result)
        self.assertIn('js/test/libs/jasmine-html.js', result)
        self.assertIn('js/test/libs/jasmine-jquery.js', result)
        self.assertNotIn('js/test/libs/jasmine.js', result)

    def test_multi_glob_expression(self):
        '''Should handle a glob pattern list as js file list'''
        files = ['js/test/libs/jasmine-*.js', 'js/test/libs/qunit-*.js']
        result = StorageGlobber.glob(files)

        self.assertIn('js/test/libs/jasmine-djangojs.js', result)
        self.assertIn('js/test/libs/jasmine-html.js', result)
        self.assertIn('js/test/libs/jasmine-jquery.js', result)
        self.assertIn('js/test/libs/qunit-tap.js', result)
        self.assertNotIn('js/test/libs/jasmine.js', result)
        self.assertNotIn('js/test/libs/qunit.js', result)

    def test_preserve_order(self):
        '''Should preserve declaration order'''
        # Orders matters: should not be an alphabeticaly sorted list
        files = ['js/test/libs/jasmine.js', 'js/djangojs/django.js', 'js/test/libs/qunit-*.js']
        result = StorageGlobber.glob(files)

        self.assertEqual(result[0], 'js/test/libs/jasmine.js')
        self.assertEqual(result[1], 'js/djangojs/django.js')

        for lib in result[2:]:
            self.assertIn('js/test/libs/qunit-', lib)
            self.assertTrue(lib.endswith('.js'))
