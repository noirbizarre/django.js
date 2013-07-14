# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class Subparser(object):
    '''
    A base class for js subcommands
    '''
    name = None
    help = None

    def __init__(self, command, subparsers):
        self.command = command
        subparser = subparsers.add_parser(self.name, help=self.help, description=self.help)
        subparser.set_defaults(func=self.handle)
        self.add_arguments(subparser)

    def add_arguments(self, parser):
        raise NotImplemented

    def handle(self, args):
        raise NotImplemented

    @property
    def stdout(self):
        return self.command.stdout

    @property
    def stderr(self):
        return self.command.stderr
