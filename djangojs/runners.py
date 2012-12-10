# -*- coding: utf-8 -*-
'''
This module provide Javascript test runners for Django unittest.
'''
import re
import sys

from os.path import join, dirname
from subprocess import Popen, STDOUT, PIPE
from tempfile import NamedTemporaryFile

from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase

from djangojs.tap import TapParser

#: Console output line length for separators
LINE_SIZE = 70

__all__ = (
    'JsTestCase',
    'JsTestException',
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
    '''
    An exception raised by Javascript tests.

    It display javascript errors into the exception message.
    '''
    def __init__(self, message, failures=[]):
        super(JsTestException, self).__init__(message)
        self.failures = failures

    def __str__(self):
        output = [super(JsTestException, self).__str__()]
        for failure in self.failures:
            message = failure.message or "expected: '%(expected)s', got: '%(got)s'" % failure.__dict__
            output.append(' + %s - %s' % (failure.parent.name, message))
            for line in failure.stack:
                # Remove jasmine/qunit entries in stack to produce smaller and more efficient output
                # TODO: find a cleaner way to improve stack trace output
                if '/js/test/libs/jasmine.js:' in line or '/js/test/libs/qunit.js:' in line:
                    continue
                output.append('\t%s' % line)
        return '\n'.join(output)


class JsTestCase(LiveServerTestCase):
    '''
    Test helper to run JS tests with PhantomJS
    '''
    #: mandatory path to the PhantomJS javascript runner
    phantomjs_runner = None
    #: an optionnal absolute URL to the test runner page
    url = None
    #: an optionnal named URL that point to the test runner page
    url_name = None
    #: an optionnal arguments array to pass to the ``reverse()`` function
    url_args = None
    #: an optionnal keyword arguments dictionnary to pass to the ``reverse()`` function
    url_kwargs = None
    #: an optionnal title for verbose console output
    title = 'PhantomJS test suite'

    def execute(self, command):
        '''
        Execute a subprocess yielding output lines
        '''
        process = Popen(command, stdout=PIPE, stderr=STDOUT, universal_newlines=True)
        while True:
            if process.poll() is not None:
                self.returncode = process.returncode
                break
            yield process.stdout.readline()

    def phantomjs(self, *args, **kwargs):
        '''
        Execute PhantomJS by giving ``args`` as command line arguments.

        If test are run in verbose mode (``-v/--verbosity`` = 2), it output:
          - the title as header (with separators before and after)
          - modules and test names
          - assertions results (with ``django.utils.termcolors`` support)

        In case of error, a JsTestException is raised to give details about javascript errors.
        '''
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
            raise JsTestException('Failed javascript assertions', failures)

    def run_suite(self):
        '''
        Run a phantomjs test suite.

         - ``phantomjs_runner`` is mandatory.
         - Either ``url`` or ``url_name`` needs to be defined.
        '''
        if not self.phantomjs_runner:
            raise JsTestException('phantomjs_runner need to be defined')
        if not (self.url or self.url_name):
            raise JsTestException('Either url or url_name need to be defined')

        if self.url_name:
            reversed_url = reverse(self.url_name, args=self.url_args, kwargs=self.url_kwargs)
            url = ''.join([self.live_server_url, reversed_url])
        else:
            url = self.url

        return self.phantomjs(self.phantomjs_runner, url, title=self.title)


class JasmineMixin(object):
    '''
    A mixin that runs a jasmine test suite with PhantomJs.
    '''
    title = 'Jasmine test suite'
    phantomjs_runner = join(dirname(__file__), 'phantomjs', 'jasmine-runner.js')

    def test(self):
        self.run_suite()


class QUnitMixin(object):
    '''
    A mixin that runs a QUnit test suite with PhantomJs.
    '''
    title = 'QUnit test suite'
    phantomjs_runner = join(dirname(__file__), 'phantomjs', 'qunit-runner.js')

    def test(self):
        self.run_suite()
