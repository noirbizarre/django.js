# -*- coding: utf-8 -*-
'''
Provide template tags to help with Javascript/Django integration.
'''
from django import template
from django.contrib.staticfiles.templatetags.staticfiles import static

from djangojs import JQUERY_VERSION
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
            except template.TemplateSyntaxError, e:
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
    return '<script type="text/javascript" src="%sjs/libs/%s"></script>' % (settings.STATIC_URL, filename)


@register.simple_tag
def javascript(filename):
    '''A simple shortcut to render a ``script`` tag to a static javascript file'''
    return '<script type="text/javascript" src="%s"></script>' % static(filename)


@register.simple_tag
def js(filename):
    '''A simple shortcut to render a ``script`` tag to a static javascript file'''
    return javascript(filename)


@register.simple_tag
def css(filename):
    '''A simple shortcut to render a ``link`` tag to a static CSS file'''
    return '<link rel="stylesheet" type="text/css" href="%s" />' % static(filename)


@register.simple_tag
def jquery_js():
    '''A shortcut to render a ``script`` tag for the packaged jQuery'''
    return js_lib('jquery-%s.min.js' % JQUERY_VERSION)


@register.inclusion_tag('djangojs/django_js_tag.html', takes_context=True)
def django_js(context, jquery=True, i18n=True, crsf=True):
    '''Include Django.js javascript library in the page'''
    return {
        'js': {
            'jquery': jquery,
            'i18n': i18n,
            'crsf': crsf,
        }
    }
