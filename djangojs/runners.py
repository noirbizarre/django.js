# -*- coding: utf-8 -*-
'''
This module provide Javascript test runners for Django unittest.
'''
import os
import re
import sys

from os.path import join, dirname
from subprocess import Popen, STDOUT, PIPE
from tempfile import NamedTemporaryFile, mkstemp

from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.test import LiveServerTestCase

from djangojs.tap import TapParser

from unittest import TestCase

#: Console output line length for separators
LINE_SIZE = 70

__all__ = (
    'JsTestCase',
    'JsFileTestCase',
    'JsTemplateTestCase',
    'JsTestException',
    'JasmineSuite',
    'QUnitSuite',
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


class PhantomJsRunner(object):
    '''
    Test helper to run JS tests with PhantomJS
    '''
    #: mandatory path to the PhantomJS javascript runner
    phantomjs_runner = None
    #: an optionnal absolute URL to the test runner page
    url = None
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

        url = self.get_url()

        self.phantomjs(self.phantomjs_runner, url, title=self.title)
        self.cleanup()

    def get_url(self):
        if not self.url:
            raise JsTestException('url need to be defined')
        return self.url

    def cleanup(self):
        pass


class JsTestCase(PhantomJsRunner, LiveServerTestCase):
    '''
    A PhantomJS suite that run against the Django LiveServerTestCase
    '''
    #: a mandatory named URL that point to the test runner page
    url_name = None
    #: an optionnal arguments array to pass to the ``reverse()`` function
    url_args = None
    #: an optionnal keyword arguments dictionnary to pass to the ``reverse()`` function
    url_kwargs = None

    def get_url(self):
        if not self.url_name:
            raise JsTestException('url_name need to be defined')

        reversed_url = reverse(self.url_name, args=self.url_args, kwargs=self.url_kwargs)
        return ''.join([self.live_server_url, reversed_url])


class JsFileTestCase(PhantomJsRunner, TestCase):
    '''
    A PhantomJS suite that run against a local html file
    '''
    #: absolute path to the test runner page
    filename = None

    def get_url(self):
        if not self.filename:
            raise JsTestException('filename need to be defined')

        return 'file://%s' % self.filename


class JsTemplateTestCase(JsFileTestCase):
    '''
    A PhantomJS suite that run against a rendered html file but without server.
    '''
    #: absolute path to the test runner page
    template_name = None

    def get_url(self):
        if not self.template_name:
            raise JsTestException('template_name need to be defined')

        fd, self.filename = mkstemp()
        os.fdopen(fd, 'w').write(render_to_string(self.template_name, {}))
        return super(JsTemplateTestCase, self).get_url()

    def cleanup(self):
        os.remove(self.filename)


class JasmineSuite(object):
    '''
    A mixin that runs a jasmine test suite with PhantomJs.
    '''
    title = 'Jasmine test suite'
    phantomjs_runner = join(dirname(__file__), 'phantomjs', 'jasmine-runner.js')
    template_name = 'djangojs/jasmine-runner.html'

    def test(self):
        self.run_suite()


class QUnitSuite(object):
    '''
    A mixin that runs a QUnit test suite with PhantomJs.
    '''
    title = 'QUnit test suite'
    phantomjs_runner = join(dirname(__file__), 'phantomjs', 'qunit-runner.js')
    template_name = 'djangojs/qunit-runner.html'

    def test(self):
        self.run_suite()
