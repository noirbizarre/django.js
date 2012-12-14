import unittest

from djangojs.tap import TapParser, TapTest, TapModule, TapAssertion


class TapAssertionTest(unittest.TestCase):
    def test_parse_ok(self):
        '''Should parse a simple OK assertion'''
        assertion = TapAssertion.parse('ok 1')
        self.assertIsNotNone(assertion)
        self.assertEqual(assertion.num, 1)
        self.assertEqual(assertion.success, True)
        self.assertEqual(assertion.parsed_indent, '')
        self.assertEqual(assertion.message, None)
        self.assertEqual(assertion.expected, None)
        self.assertEqual(assertion.got, None)
        self.assertListEqual(assertion.stack, [])

    def test_parse_not_ok(self):
        '''Should parse a simple NOT OK assertion'''
        assertion = TapAssertion.parse('not ok 2')
        self.assertIsNotNone(assertion)
        self.assertEqual(assertion.num, 2)
        self.assertEqual(assertion.success, False)
        self.assertEqual(assertion.parsed_indent, '')
        self.assertEqual(assertion.message, None)
        self.assertEqual(assertion.expected, None)
        self.assertEqual(assertion.got, None)
        self.assertListEqual(assertion.stack, [])

    def test_parse_ok_with_message(self):
        '''Should parse an OK assertion with message'''
        assertion = TapAssertion.parse('ok 284 - I should be equal to me.')
        self.assertIsNotNone(assertion)
        self.assertEqual(assertion.num, 284)
        self.assertEqual(assertion.success, True)
        self.assertEqual(assertion.parsed_indent, '')
        self.assertEqual(assertion.message, 'I should be equal to me.')
        self.assertEqual(assertion.expected, None)
        self.assertEqual(assertion.got, None)
        self.assertListEqual(assertion.stack, [])

    def test_parse_not_ok_with_message(self):
        '''Should parse a NOT OK assertion with message'''
        assertion = TapAssertion.parse('not ok 284 - I should be equal to me.')
        self.assertIsNotNone(assertion)
        self.assertEqual(assertion.num, 284)
        self.assertEqual(assertion.success, False)
        self.assertEqual(assertion.parsed_indent, '')
        self.assertEqual(assertion.message, 'I should be equal to me.')
        self.assertEqual(assertion.expected, None)
        self.assertEqual(assertion.got, None)
        self.assertListEqual(assertion.stack, [])

    def test_parse_not_ok_with_source(self):
        '''Should parse a NOT OK assertion with message and source'''
        input = 'not ok 298 - reset should not modify test status, source: at http://localhost:8000/static/js/test/libs/qunit.js:435'

        assertion = TapAssertion.parse(input)

        self.assertIsNotNone(assertion)
        self.assertEqual(assertion.num, 298)
        self.assertEqual(assertion.success, False)
        self.assertEqual(assertion.parsed_indent, '')
        self.assertEqual(assertion.message, 'reset should not modify test status')
        self.assertEqual(assertion.expected, None)
        self.assertEqual(assertion.got, None)
        self.assertListEqual(assertion.stack, ['http://localhost:8000/static/js/test/libs/qunit.js:435'])

    def test_parse_not_ok_with_expectations(self):
        '''Should parse a NOT OK assertion with expectations'''
        input = "not ok 42 - expected: 'something', got: 'something else'"

        assertion = TapAssertion.parse(input)

        self.assertIsNotNone(assertion)
        self.assertEqual(assertion.num, 42)
        self.assertEqual(assertion.success, False)
        self.assertEqual(assertion.parsed_indent, '')
        self.assertEqual(assertion.message, None)
        self.assertEqual(assertion.expected, 'something')
        self.assertEqual(assertion.got, 'something else')
        self.assertListEqual(assertion.stack, [])

    def test_parse_not_ok_with_all(self):
        '''Should parse a NOT OK assertion with all extras'''
        input = "not ok 42 - reset should not modify test status, expected: 'something', got: 'something else', source: at http://localhost:8000/static/js/test/libs/qunit.js:435"

        assertion = TapAssertion.parse(input)

        self.assertIsNotNone(assertion)
        self.assertEqual(assertion.num, 42)
        self.assertEqual(assertion.success, False)
        self.assertEqual(assertion.parsed_indent, '')
        self.assertEqual(assertion.message, 'reset should not modify test status')
        self.assertEqual(assertion.expected, 'something')
        self.assertEqual(assertion.got, 'something else')
        self.assertListEqual(assertion.stack, ['http://localhost:8000/static/js/test/libs/qunit.js:435'])


class TapTestTest(unittest.TestCase):
    def test_parse_test(self):
        '''Should parse a test statement'''
        input = '# test: This is a test'

        test = TapTest.parse(input)

        self.assertEqual(test.name, 'This is a test')
        self.assertEqual(test.parsed_indent, '')


class TapModuleTest(unittest.TestCase):
    def test_parse_module(self):
        '''Should parse a module statement'''
        input = '# module: This is a module'

        module = TapModule.parse(input)

        self.assertEqual(module.name, 'This is a module')
        self.assertEqual(module.parsed_indent, '')


class TapParserTest(unittest.TestCase):
    def test_single_test(self):
        '''a single test should output TapAssertion and TapTast'''

        parser = TapParser(TapTest)
        output = '''
# test: should be defined
ok 1
        '''

        for item in parser.parse(output):
            print item.display()
