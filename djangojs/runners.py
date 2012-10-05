# -*- coding: utf-8 -*-
from os.path import join, dirname
from subprocess import call
from tempfile import NamedTemporaryFile

from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase


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

        with NamedTemporaryFile(delete=True) as cookies_file:
            cmd = ('phantomjs', '--cookies-file=%s' % cookies_file.name) + args
            result = call(cmd)

        print separator
        return result

    def run_jasmine_suite(self, runner_url_name, title='Jasmine test suite'):
        jasmine_runner_url = ''.join([self.live_server_url, reverse(runner_url_name)])
        phantomjs_jasmine_runner = join(dirname(__file__), 'phantomjs', 'run-jasmine.js')

        return self.phantomjs(phantomjs_jasmine_runner, jasmine_runner_url, title=title)

    def run_qunit_suite(self, runner_url_name, title='Qunit test suite'):
        qunit_runner_url = ''.join([self.live_server_url, reverse(runner_url_name)])
        phantomjs_qunit_runner = join(dirname(__file__), 'phantomjs', 'run-qunit.js')

        return self.phantomjs(phantomjs_qunit_runner, qunit_runner_url, title=title)
