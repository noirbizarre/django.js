# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import re

from glob import iglob

from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import CommandError
from djangojs.management.commands.subparser import Subparser


class LocalizeParser(Subparser):
    '''
    A command handling localization.
    '''
    name = 'localize'
    help = 'Generate PO file from js files'

    def add_arguments(self, parser):
        parser.add_argument('apps', nargs='*', metavar='app', help="Applications to localize")
        parser.add_argument('--locale', '-l',
            help='Creates or updates the message files for the given locale (e.g. pt_BR).'),
        parser.add_argument('--all', '-a', action='store_true',
            help='Updates the message files for all existing locales.'),
        parser.add_argument('--extension', '-e', dest='extensions', default=['js'], action='append',
            help=('The file extension(s) to examine (default: "js"). '
            'Separate multiple extensions with commas, or use -e multiple times.')),
        parser.add_argument('--symlinks', '-s', action='store_true',
            help='Follows symlinks to directories when examining source code and templates for translation strings.'),
        parser.add_argument('--ignore', '-i', action='append', default=[], metavar='PATTERN',
            help='Ignore files or directories matching this glob-style pattern. Use multiple times to ignore more.'),
        parser.add_argument('--no-default-ignore', action='store_false',
            help="Don't ignore the common glob-style patterns 'CVS', '.*' and '*~'."),
        parser.add_argument('--no-wrap', action='store_true',
            help="Don't break long message lines into several lines"),
        parser.add_argument('--no-location', action='store_true',
            help="Don't write '#: filename:line' lines"),
        parser.add_argument('--no-obsolete', action='store_true', help="Remove obsolete message strings"),

    def handle(self, args):
        from django.core.management.commands.makemessages import make_messages, handle_extensions
        from django.db import models
        from djangojs.conf import settings

        if not args.apps:
            raise CommandError('Enter at least one application name.')

        if not (args.locale or args.all):
            raise CommandError('Enter a locale or use the --all switch.')

        ignore_patterns = args.ignore
        if args.no_default_ignore:
            ignore_patterns += ['CVS', '.*', '*~']
        ignore_patterns = list(set(ignore_patterns))

        extensions = handle_extensions(args.extensions)

        try:
            apps = [models.get_app(app) for app in args.apps]
        except (ImproperlyConfigured, ImportError) as e:
            raise CommandError("%s. Are you sure your INSTALLED_APPS setting is correct?" % e)

        for app in apps:
            app_dir = os.path.dirname(app.__file__)
            os.chdir(app_dir)

            catalogs = [self.build_catalog(root, ext, regexp) for ext, root, regexp in settings.JS_I18N_PATTERNS]

            make_messages(args.locale, b'djangojs', args.verbosity, args.all, extensions,
                          args.symlinks, ignore_patterns, args.no_wrap, args.no_location,
                          args.no_obsolete, self.stdout)

            for catalog in catalogs:
                os.remove(catalog)

    def build_catalog(self, root, extension, regexp):
        catalog = os.path.join(root, '{}_catalog.js'.format(extension))
        regexps = regexp if isinstance(regexp, (list, tuple)) else [regexp]
        with open(catalog, 'wb') as output:
            for _, dirnames, _ in os.walk(root):
                for dirname in [''] + dirnames:
                    glob_pattern = os.path.join(root, dirname, '*.{}'.format(extension))
                    for filename in iglob(glob_pattern):
                        content = open(filename, 'r').read()
                        for regexp in regexps:
                            for match in re.finditer(regexp, content):
                                line_no = content.count('\n', 0, match.start()) + 1
                                output.write('// Translators: {}:{}\n'.format(filename, line_no))
                                output.write('gettext(\'{}\');\n'.format(match.group(1)))
        return catalog
