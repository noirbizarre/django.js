# -*- coding: utf-8 -*-
import re
import sys

from os.path import join, dirname
from subprocess import Popen, STDOUT, PIPE
from tempfile import NamedTemporaryFile
# from collections import OrderedDict

from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase

# TAP regex
TAP_MODULE_REGEX = re.compile(r'^(?P<indent>\s*)# module: (?P<name>.*)$')
TAP_TEST_REGEX = re.compile(r'^(?P<indent>\s*)# test: (?P<name>.*)$')
TAP_ASSERTION_REGEX = re.compile(r'^(?P<indent>\s*)(?P<type>(?:not )?ok) (?P<num>\d+)(?: - (?P<details>.*))?$')
TAP_STACK_REGEX = re.compile(r'^(?P<indent>\s*)#(?:\s+)at(?P<stack>.*)$')
TAP_END_REGEX = re.compile(r'^(?P<indent>\s*)(?P<start>\d+)\.\.(?P<end>\d+)(?: - (?P<details>.*))?$')
TAP_DETAILS_REGEX = re.compile(r'^(?:expected: (?P<expected>.*), got: (?P<got>.*), )?(?:matcher: (?P<matcher>.*), )?source: at (?P<source>.*)$')

# Output format
LINE_SIZE = 70
INDENT = 4
DEFAULT_ENCODING = 'utf-8'
COLORS = {
      "green": 32,
      "red": 31,
      "yellow": 33
}


def colorize(text, color):
    return u'\033[%sm%s\033[0m' % (COLORS[color], text)


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


class TapItem(object):
    parent = None
    parsed_indent = ''

    @property
    def indent(self):
        if self.parent and isinstance(self.parent, TapItem):
            if isinstance(self.parent, TapModule):
                return self.parent.indent + ' ' * INDENT
            else:
                return self.parent.indent
        return ''


class TapGroup(list, TapItem):
    def __init__(self, name='', parent=None, parsed_indent='', *args, **kwargs):
        super(TapGroup, self).__init__(*args, **kwargs)
        self.name = name
        self.parent = parent
        self.parsed_indent = parsed_indent

    def __unicode__(self):
        return u'%s: %s' % (self.name, super(TapGroup, self).__unicode__())

    def __str__(self):
        return unicode(self).encode(sys.stdout.encoding or DEFAULT_ENCODING, 'replace')

    def __nonzero__(self):
        return True

    def append(self, item):
        if isinstance(item, (TapGroup, TapAssertion)) and not item.parent:
            item.parent = self
        super(TapGroup, self).append(item)


class TapModule(TapGroup):

    def display(self):
        return u'%s%s' % (self.indent, self.name)

    def __unicode__(self):
        return u'# module: %s' % self.name

    @classmethod
    def parse(cls, line):
        match = TAP_MODULE_REGEX.match(line.rstrip())
        if match:
            return cls(
                match.group('name').strip(),
                parsed_indent=match.group('indent')
            )
        else:
            return None


class TapTest(TapGroup):

    def display(self):
        assertions = [result.display(True) for result in self]
        if assertions:
            return u'%s%s (%s)' % (self.indent, self.name, ' '.join(assertions))
        else:
            return u'%s%s' % (self.indent, self.name)

    def __unicode__(self):
        return u'# test: %s' % self.name

    @classmethod
    def parse(cls, line):
        match = TAP_TEST_REGEX.match(line.rstrip())
        if match:
            return cls(match.group('name').strip(), parsed_indent=match.group('indent'))
        else:
            return None


class TapAssertion(TapItem):
    def __init__(self, num, success=True, msg=None, parsed_indent='', *args, **kwargs):
        super(TapAssertion, self).__init__()
        self.num = num
        self.success = success
        self.msg = msg
        self.expected = None
        self.got = None
        self.matcher = None
        self.stack = None
        self.parsed_indent = parsed_indent

    def display(self, inline=False):
        if inline:
            return colorize(u'ok', 'green') if self.success else colorize(u'ko', 'red')
        else:
            text = self.indent
            if self.success:
                text += colorize(u'ok %s' % self.num, 'green')
            else:
                text += colorize(u'not ok %s' % self.num, 'red')
            text = '%s - %s' % (text, self.msg) if self.msg else text
            if self.expected is not None and self.got is not None:
                text = '\n'.join([text, '# expected: %s' % self.expected, '# got: %s' % self.got])
            if self.stack:
                text = '\n'.join([text, '\n'.join(['# stack: %s' % line for line in self.stack])])
            return text

    def __unicode__(self):
        return u'ok %s' % self.num if self.success else u'not ok %s' % self.num

    def __str__(self):
        return unicode(self).encode(sys.stdout.encoding or DEFAULT_ENCODING, 'replace')

    @classmethod
    def parse(cls, line):
        match = TAP_ASSERTION_REGEX.match(line.rstrip())
        if match:
            assertion = TapAssertion(
                match.group('num'),
                match.group('type') == 'ok',
                parsed_indent=match.group('indent')
            )
            if match.group('details'):
                details_match = TAP_DETAILS_REGEX.match(match.group('details'))
                if details_match and details_match.group('expected'):
                    assertion.expected = details_match.group('expected')
                    assertion.got = details_match.group('got')
                if details_match and details_match.group('matcher'):
                    assertion.matcher = details_match.group('matcher')
                if details_match:
                    assertion.stack = [details_match.group('source')]
                else:
                    assertion.msg = match.group('details')
            return assertion
        else:
            return None


HIERARCHY = (
    TapModule,
    TapTest,
    TapAssertion,
)


def hierarchy(item):
    if not isinstance(item, TapItem):
        raise ValueError('Item should be a TapItem')
    return HIERARCHY.index(item.__class__)


class TapOutputParser(object):
    def __init__(self, proc, yield_class=TapTest):
        if not issubclass(yield_class, TapItem):
            raise ValueError('yield class should extend TapItem')
        self.proc = proc
        self.suites = TapGroup()
        self.current = self.suites
        self.yield_class = yield_class

    def parse(self):
        while self.proc.poll() is None:
            for item in self.parse_line(self.proc.stdout.readline()):
                yield item

        for item in self.get_lasts():
            yield item

    def parse_line(self, line):
        item = TapModule.parse(line) or TapTest.parse(line) or TapAssertion.parse(line)
        if item is not None:
            return self.set_current(item)

        match = TAP_STACK_REGEX.match(line.rstrip())
        if match:
            self.current.stack.append(match.group('stack'))
            return []

        match = TAP_END_REGEX.match(line.rstrip())
        if match and VERBOSITY > 2:
            print '# end %s-%s' % (match.group('start'), match.group('end'))
            return []

        if line and VERBOSITY > 2:
            print 'not matched: %s' % line

        return []

    def set_current(self, item=None):
        if item and not isinstance(item, TapItem):
            raise ValueError('Should be a TAP item')

        ended = []

        while self.current.parent and hierarchy(item) < hierarchy(self.current):
            if isinstance(self.current, self.yield_class):
                ended.append(self.current)
            self.current = self.current.parent

        while self.current.parent \
                and hierarchy(item) == hierarchy(self.current) \
                and len(item.parsed_indent) <= len(self.current.parsed_indent):
            if isinstance(self.current, self.yield_class):
                ended.append(self.current)
            self.current = self.current.parent

        self.current.append(item)
        self.current = item

        if hierarchy(self.current) < HIERARCHY.index(self.yield_class):
            ended.append(self.current)

        return ended

    def get_lasts(self):
        lasts = []
        while isinstance(self.current, TapItem) and self.current.parent:
            if isinstance(self.current, self.yield_class):
                lasts.append(self.current)
            self.current = self.current.parent
        return lasts


class JsTestCase(LiveServerTestCase):
    '''
    Test helper to run JS test (Jasmine/Qunit) with phantomjs
    '''

    def phantomjs(self, *args, **kwargs):
        separator = '=' * LINE_SIZE
        title = kwargs['title'] if 'title' in kwargs else 'phantomjs output'
        nb_spaces = (LINE_SIZE - len(title)) / 2

        if VERBOSE:
            print ''
            print separator
            print ' ' * nb_spaces + title
            print separator

        with NamedTemporaryFile(delete=True) as cookies_file:
            cmd = ('phantomjs', '--cookies-file=%s' % cookies_file.name) + args
            proc = Popen(cmd, stdout=PIPE, stderr=STDOUT, universal_newlines=True)
            parser = TapOutputParser(proc)

            for item in parser.parse():
                if VERBOSE:
                    print item.display()

        if VERBOSE:
            print separator

        self.assertEqual(proc.returncode, 0)

    def run_jasmine(self, runner_url_name, title='Jasmine test suite'):
        jasmine_runner_url = ''.join([self.live_server_url, reverse(runner_url_name)])
        phantomjs_jasmine_runner = join(dirname(__file__), 'phantomjs', 'jasmine-runner.js')

        return self.phantomjs(phantomjs_jasmine_runner, jasmine_runner_url, title=title)

    def run_qunit(self, runner_url_name, title='Qunit test suite'):
        qunit_runner_url = ''.join([self.live_server_url, reverse(runner_url_name)])
        phantomjs_qunit_runner = join(dirname(__file__), 'phantomjs', 'qunit-runner.js')  # 'run-qunit.js')

        return self.phantomjs(phantomjs_qunit_runner, qunit_runner_url, title=title)
