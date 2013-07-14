# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from djangojs.management.commands.subparser import Subparser


class LauncherParser(Subparser):
    name = 'launcher'
    help = 'Get a PhantomJS launcher path'

    def add_arguments(self, parser):
        parser.add_argument('name', help='Runner name')

    def handle(self, args):
        from djangojs.runners import LAUNCHERS
        launcher = args.name.lower()
        try:
            self.stdout.write(LAUNCHERS[launcher])
        except KeyError:
            self.stderr.write('Unknown launcher "%s"' % launcher)
