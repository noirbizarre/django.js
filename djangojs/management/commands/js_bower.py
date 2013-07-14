# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from os.path import exists

from django.core.management.base import CommandError
from djangojs.management.commands.subparser import Subparser


class BowerParser(Subparser):
    name = 'bower'
    help = 'Generate a .bowerrc file'

    def add_arguments(self, parser):
        parser.add_argument('target', help='The target directory for bower downloads')
        parser.add_argument('-f', '--force', action='store_true', help='Overwrite the file if exists')

    def handle(self, args):
        filename = '.bowerrc'
        if exists(filename) and not args.force:
            raise CommandError('.bowerrc file already exists. Use --force to overwrite')

        target = args.target if args.target.endswith('/') else '{}/'.format(args.target)
        bowerrc = {
            'directory': './{}'.format(target)
        }

        with open(filename, 'w') as output:
            output.write(json.dumps(bowerrc))
            output.write('\n')

        self.stdout.write('Created .bowerrc file into the current directory')
