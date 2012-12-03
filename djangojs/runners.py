# -*- coding: utf-8 -*-
import re
import sys

from os.path import join, dirname
from subprocess import Popen, STDOUT, PIPE
from tempfile import NamedTemporaryFile

from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase

from djangojs.tap import TapParser

# Output format
LINE_SIZE = 70

__all__ = (
    'JsTestCase',
    'JasmineMixin',
    'QUnitMixin',
)


def parse_verbosity():
    verbosity = 1
    regex = re.compile(r'(?:-v|--verbosity)(?:(?:\=)?([0-3]))?')
    for idx, arg in enumerate(sys.argv):
        match = regex.match(arg)
        if match:
            verbosity = int(match.group(1)) if match.group(1) else int(sys.argv[idx + 1])
            break
    return verbosity

VERBOSITY = parse_verbosity()
VERBOSE = VERBOSITY > 1


class JsTestException(Exception):
    def __init__(self, message, failures=[]):
        super(JsTestException, self).__init__(message)
        self.failures = failures

    def __str__(self):
        output = '\n'.join(
            [super(JsTestException, self).__str__()] +
            ['\t%s' % failure.message for failure in self.failures]
        )
        return output


class JsTestCase(LiveServerTestCase):
    '''
    Test helper to run JS tests with phantomjs
    '''
    runner_url = None
    runner_url_name = None
    title = 'PhantomJS test suite'

    def execute(self, command):
        process = Popen(command, stdout=PIPE, stderr=STDOUT, universal_newlines=True)
        while True:
            if process.poll() is not None:
                self.returncode = process.returncode
                break
            yield process.stdout.readline()

    def phantomjs(self, *args, **kwargs):
        separator = '=' * LINE_SIZE
        title = kwargs['title'] if 'title' in kwargs else 'phantomjs output'
        nb_spaces = (LINE_SIZE - len(title)) / 2

        if VERBOSE:
            print ''
            print separator
            print ' ' * nb_spaces + title
            print separator
            sys.stdout.flush()

        with NamedTemporaryFile(delete=True) as cookies_file:
            cmd = ('phantomjs', '--cookies-file=%s' % cookies_file.name) + args
            parser = TapParser(debug=VERBOSITY > 2)
            output = self.execute(cmd)

            for item in parser.parse(output):
                if VERBOSE:
                    print item.display()
                    sys.stdout.flush()

        if VERBOSE:
            print separator
            sys.stdout.flush()

        failures = parser.suites.get_all_failures()
        if failures:
            raise JsTestException('%s JS tests failed' % len(failures), failures)

    def run_suite(self):
        '''
        Run a phantomjs test suite.
        '''
        if not self.phantomjs_runner:
            raise JsTestException('phantomjs_runner need to be defined')
        if not (self.runner_url or self.runner_url_name):
            raise JsTestException('Either runner_url or runner_url_name need to be defined')

        runner_url = self.runner_url or ''.join([self.live_server_url, reverse(self.runner_url_name)])

        return self.phantomjs(self.phantomjs_runner, runner_url, title=self.title)


class JasmineMixin(object):
    '''
    Run a jasmine test suite.
    '''
    title = 'Jasmine test suite'
    phantomjs_runner = join(dirname(__file__), 'phantomjs', 'jasmine-runner.js')

    def test(self):
        self.run_suite()


class QUnitMixin(object):
    '''
    Run a QUnit test suite.
    '''
    title = 'QUnit test suite'
    phantomjs_runner = join(dirname(__file__), 'phantomjs', 'qunit-runner.js')

    def test(self):
        self.run_suite()
