# -*- coding: utf-8 -*-
'''
Provide template tags to help with Javascript/Django integration.
'''
from __future__ import unicode_literals

from django import template
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils import six

from djangojs import JQUERY_MIGRATE_VERSION
from djangojs.conf import settings

register = template.Library()


def verbatim_tags(parser, token, endtagname):
    '''
    Javascript templates (jquery, handlebars.js, mustache.js) use constructs like:

    ::

        {{if condition}} print something{{/if}}

    This, of course, completely screws up Django templates,
    because Django thinks {{ and }} means something.

    The following code preserves {{ }} tokens.

    This version of verbatim template tag allows you to use tags
    like url {% url name %}. {% trans "foo" %} or {% csrf_token %} within.

    Inspired by:
     - Miguel Araujo: https://gist.github.com/893408
    '''
    text_and_nodes = []
    while 1:
        token = parser.tokens.pop(0)
        if token.contents == endtagname:
            break

        if token.token_type == template.TOKEN_VAR:
            text_and_nodes.append('{{')
            text_and_nodes.append(token.contents)

        elif token.token_type == template.TOKEN_TEXT:
            text_and_nodes.append(token.contents)

        elif token.token_type == template.TOKEN_BLOCK:
            try:
                command = token.contents.split()[0]
            except IndexError:
                parser.empty_block_tag(token)

            try:
                compile_func = parser.tags[command]
            except KeyError:
                parser.invalid_block_tag(token, command, None)
            try:
                node = compile_func(parser, token)
            except template.TemplateSyntaxError as e:
                if not parser.compile_function_error(token, e):
                    raise
            text_and_nodes.append(node)

        if token.token_type == template.TOKEN_VAR:
            text_and_nodes.append('}}')

    return text_and_nodes


class VerbatimNode(template.Node):
    '''
    Wrap {% verbatim %} and {% endverbatim %} around a
    block of javascript template and this will try its best
    to output the contents with no changes.

    ::

        {% verbatim %}
            {% trans "Your name is" %} {{first}} {{last}}
        {% endverbatim %}
    '''
    def __init__(self, text_and_nodes):
        self.text_and_nodes = text_and_nodes

    def render(self, context):
        output = ""
        # If its text we concatenate it, otherwise it's a node and we render it
        for bit in self.text_and_nodes:
            if isinstance(bit, basestring):
                output += bit
            else:
                output += bit.render(context)
        return output


@register.tag
def verbatim(parser, token):
    '''Renders verbatim tags'''
    text_and_nodes = verbatim_tags(parser, token, 'endverbatim')
    return VerbatimNode(text_and_nodes)


@register.simple_tag
def js_lib(filename):
    return javascript('js/libs/%s' % filename)


@register.simple_tag
def javascript(filename, type='text/javascript'):
    '''A simple shortcut to render a ``script`` tag to a static javascript file'''
    if '?' in filename and len(filename.split('?')) is 2:
        filename, params = filename.split('?')
        return '<script type="%s" src="%s?%s"></script>' % (type, staticfiles_storage.url(filename), params)
    else:
        return '<script type="%s" src="%s"></script>' % (type, staticfiles_storage.url(filename))


@register.simple_tag
def js(filename, type='text/javascript'):
    '''A simple shortcut to render a ``script`` tag to a static javascript file'''
    return javascript(filename, type=type)


@register.simple_tag
def coffeescript(filename):
    '''A simple shortcut to render a ``script`` tag to a static coffeescript file'''
    return javascript(filename, type='text/coffeescript')


@register.simple_tag
def coffee(filename):
    '''A simple shortcut to render a ``script`` tag to a static coffeescript file'''
    return javascript(filename, type='text/coffeescript')


@register.simple_tag
def css(filename):
    '''A simple shortcut to render a ``link`` tag to a static CSS file'''
    return '<link rel="stylesheet" type="text/css" href="%s" />' % staticfiles_storage.url(filename)


def _boolean(value):
    if isinstance(value, bool):
        return value
    elif isinstance(value, (six.text_type, six.string_types)):
        return value.lower() == 'true'
    elif isinstance(value, int):
        return value != 0
    else:
        return False


@register.simple_tag
def jquery_js(version=None, migrate=False):
    '''A shortcut to render a ``script`` tag for the packaged jQuery'''
    version = version or settings.JQUERY_VERSION
    suffix = '.min' if not settings.DEBUG else ''
    libs = [js_lib('jquery-%s%s.js' % (version, suffix))]
    if _boolean(migrate):
        libs.append(js_lib('jquery-migrate-%s%s.js' % (JQUERY_MIGRATE_VERSION, suffix)))
    return '\n'.join(libs)


@register.inclusion_tag('djangojs/django_js_tag.html', takes_context=True)
def django_js(context, jquery=True, i18n=True, csrf=True, init=True):
    '''Include Django.js javascript library in the page'''
    return {
        'js': {
            'minified': not settings.DEBUG,
            'jquery': _boolean(jquery),
            'i18n': _boolean(i18n),
            'csrf': _boolean(csrf),
            'init': _boolean(init),
        }
    }


@register.inclusion_tag('djangojs/django_js_init.html', takes_context=True)
def django_js_init(context, jquery=False, i18n=True, csrf=True, init=True):
    '''Include Django.js javascript library initialization in the page'''
    return {
        'js': {
            'jquery': _boolean(jquery),
            'i18n': _boolean(i18n),
            'csrf': _boolean(csrf),
            'init': _boolean(init),
        }
    }
