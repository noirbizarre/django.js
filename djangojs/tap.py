# -*- coding: utf-8 -*-
'''
This module provide test runners for JS in Django.
'''
from __future__ import unicode_literals

import re

from django.utils import termcolors
from django.utils.encoding import python_2_unicode_compatible

green = termcolors.make_style(fg='green', opts=('bold',))
red = termcolors.make_style(fg='red', opts=('bold',))

# TAP regex
TAP_MODULE_REGEX = re.compile(r'^(?P<indent>\s*)# module: (?P<name>.*)$')
TAP_TEST_REGEX = re.compile(r'^(?P<indent>\s*)# test: (?P<name>.*)$')
TAP_ASSERTION_REGEX = re.compile(r'^(?P<indent>\s*)(?P<type>(?:not )?ok) (?P<num>\d+)(?: - (?P<details>.*))?$')
TAP_STACK_REGEX = re.compile(r'^(?P<indent>\s*)#\s+at\s+(?P<stack>.*)$')
TAP_END_REGEX = re.compile(r'^(?P<indent>\s*)(?P<start>\d+)\.\.(?P<end>\d+)(?: - (?P<details>.*))?$')
TAP_DETAILS_REGEX = re.compile(
    r'''^(?:(?P<message>(?!expected)(?!got)(?!matcher)(?!source).+?)(?:, )?)?'''
    r'''(?:expected: '(?P<expected>.+)', got: '(?P<got>.+?)'(?:, )?)?'''
    r'''(?:matcher: '(?P<matcher>.+?)'(?:, )?)?'''
    r'''(?:source:\s+at\s+(?P<source>.+?))?$''')


# Output format
INDENT = 4
DEFAULT_ENCODING = 'utf-8'


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


@python_2_unicode_compatible
class TapGroup(list, TapItem):
    def __init__(self, name='', parent=None, parsed_indent='', *args, **kwargs):
        super(TapGroup, self).__init__(*args, **kwargs)
        self.name = name
        self.parent = parent
        self.parsed_indent = parsed_indent

    def __str__(self):
        return '# Groupe %s' % self.name

    def __nonzero__(self):
        return True

    def __bool__(self):
        return True

    def append(self, item):
        if isinstance(item, (TapGroup, TapAssertion)) and not item.parent:
            item.parent = self
        super(TapGroup, self).append(item)

    def get_all_failures(self):
        failures = []
        for item in self:
            if isinstance(item, TapGroup):
                failures.extend(item.get_all_failures())
            elif isinstance(item, TapAssertion) and not item.success:
                failures.append(item)
        return failures


@python_2_unicode_compatible
class TapModule(TapGroup):

    def display(self):
        return '%s%s' % (self.indent, self.name)

    def __str__(self):
        return '# module: %s' % self.name

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


@python_2_unicode_compatible
class TapTest(TapGroup):

    def display(self):
        assertions = [result.display(True) for result in self]
        if assertions:
            return '%s%s (%s)' % (self.indent, self.name, ' '.join(assertions))
        else:
            return '%s%s' % (self.indent, self.name)

    def __str__(self):
        return '# test: %s' % self.name

    @classmethod
    def parse(cls, line):
        match = TAP_TEST_REGEX.match(line.rstrip())
        if match:
            return cls(match.group('name').strip(), parsed_indent=match.group('indent'))
        else:
            return None


@python_2_unicode_compatible
class TapAssertion(TapItem):
    def __init__(self, num, success=True, message=None, parsed_indent='', *args, **kwargs):
        super(TapAssertion, self).__init__()
        self.num = num
        self.success = success
        self.message = message
        self.expected = None
        self.got = None
        self.matcher = None
        self.stack = []
        self.parsed_indent = parsed_indent

    def display(self, inline=False):
        if inline:
            return green('ok') if self.success else red('ko')
        else:
            text = self.indent
            if self.success:
                text += green('ok %s' % self.num)
            else:
                text += red('not ok %s' % self.num)
            text = '%s - %s' % (text, self.message) if self.message else text
            if self.expected is not None and self.got is not None:
                text = '\n'.join([text, '# expected: %s' % self.expected, '# got: %s' % self.got])
            if self.stack:
                text = '\n'.join([text] + ['# stack: %s' % line for line in self.stack])
            return text

    def __str__(self):
        return 'ok %s' % self.num if self.success else 'not ok %s' % self.num

    @classmethod
    def parse(cls, line):
        match = TAP_ASSERTION_REGEX.match(line.rstrip())
        if match:
            assertion = cls(
                int(match.group('num')),
                match.group('type') == 'ok',
                parsed_indent=match.group('indent')
            )
            if match.group('details'):
                details_match = TAP_DETAILS_REGEX.match(match.group('details'))
                if details_match and details_match.group('message'):
                    assertion.message = details_match.group('message')
                if details_match and details_match.group('expected'):
                    assertion.expected = details_match.group('expected')
                    assertion.got = details_match.group('got')
                if details_match and details_match.group('matcher'):
                    assertion.matcher = details_match.group('matcher')
                if details_match and details_match.group('source'):
                    assertion.stack = [details_match.group('source')]
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


class TapParser(object):
    '''
    A TAP parser class reading from iterable TAP lines.
    '''
    def __init__(self, yield_class=TapTest, debug=False):
        if not issubclass(yield_class, TapItem):
            raise ValueError('yield class should extend TapItem')
        self.suites = TapGroup()
        self.current = self.suites
        self.yield_class = yield_class
        self.debug = debug

    def parse(self, lines):
        for line in lines:
            for item in self.parse_line(line):
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
        if match and self.debug:
            print('# end %s-%s' % (match.group('start'), match.group('end')))
            return []

        if line and self.debug:
            print('not matched: %s' % line)

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
