# -*- coding: utf-8 -*-
'''
Main access point for all JS commands
'''
import argparse
import logging
import sys

from django.core.management.base import BaseCommand, handle_default_options
try:
    from django.core.management.base import OutputWrapper
except:
    pass

from djangojs.management.commands.js_localize import LocalizeParser
from djangojs.management.commands.js_launcher import LauncherParser
from djangojs.management.commands.js_bower import BowerParser

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Handle javascript operations'
    args = 'command'
    requires_model_validation = False
    can_import_settings = True
    subparsers = (
        BowerParser,
        LauncherParser,
        LocalizeParser,
    )

    def usage(self, subcommand):
        return self.create_parser('', subcommand).format_usage()

    def run_from_argv(self, argv):
        """
        Set up any environment changes requested (e.g., Python path
        and Django settings), then run this command. If the
        command raises a ``CommandError``, intercept it and print it sensibly
        to stderr.
        """
        parser = self.create_parser(argv[0], argv[1])
        args = parser.parse_args(argv[2:])
        handle_default_options(args)
        try:
            self.execute(args)
        except Exception as e:
            # self.stderr is not guaranteed to be set here
            try:
                fallback_stderr = OutputWrapper(sys.stderr, self.style.ERROR)
            except:
                fallback_stderr = self.stdout
            stderr = getattr(self, 'stderr', fallback_stderr)
            if args.traceback:
                stderr.write(traceback.format_exc())
            else:
                stderr.write('%s: %s' % (e.__class__.__name__, e))
            sys.exit(1)

    def create_parser(self, prog_name, subcommand):
        """
        Create and return the ``OptionParser`` which will be used to
        parse the arguments to this command.

        """
        parser = argparse.ArgumentParser(prog='%s %s' % (prog_name, subcommand), description=self.help)

        parser.add_argument('-v', '--verbosity', action='store', default=1, type=int, choices=range(4),
            help='Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output'),
        parser.add_argument('--settings',
            help='The Python path to a settings module, e.g. "myproject.settings.main". '
            'If this isn\'t provided, the DJANGO_SETTINGS_MODULE environment variable will be used.'),
        parser.add_argument('--pythonpath',
            help='A directory to add to the Python path, e.g. "/home/djangoprojects/myproject".'),
        parser.add_argument('--traceback', action='store_true', help='Print traceback on exception'),

        subparsers = parser.add_subparsers(description='JavaScript command to execute')

        for subparser in self.subparsers:
            subparser(self, subparsers)

        return parser

    def print_help(self, prog_name, subcommand):
        parser = self.create_parser(prog_name, subcommand)
        parser.print_help()

    def handle(self, args):
        args.func(args)
