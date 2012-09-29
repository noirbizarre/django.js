import json

from os.path import join, dirname
from subprocess import call

from django.test import LiveServerTestCase, TestCase
from django.core.urlresolvers import reverse


class JsTestCase(LiveServerTestCase):

    def phantomjs(self, *args, **kwargs):
        LINE_SIZE = 70
        separator = '=' * LINE_SIZE
        title = kwargs['title'] if 'title' in kwargs else 'phantomjs output'
        nb_spaces = (LINE_SIZE - len(title)) / 2
        print ''
        print separator
        print ' ' * nb_spaces + title
        print separator
        cmd = ('phantomjs',) + args
        result = call(cmd)
        print separator
        return result


class JasmineTests(JsTestCase):

    def test_jasmine_suite(self):
        '''It shoudl run its its own Jasmine test suite'''
        jasmine_runner_url = ''.join([self.live_server_url, reverse('jasmine_runner')])
        phantomjs_jasmine_runner = join(dirname(__file__), 'phantomjs', 'run-jasmine.js')

        result = self.phantomjs(phantomjs_jasmine_runner, jasmine_runner_url, title='Jasmine test suite')

        self.assertEqual(0, result)


class DjangoJsJsonTest(TestCase):

    def test_should_render(self):
        '''It should render a JSON URLs descriptor'''
        response = self.client.get(reverse('django_js_json'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
