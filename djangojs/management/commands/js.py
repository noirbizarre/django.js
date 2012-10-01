# -*- coding: utf-8 -*-
'''
Main access point for all JS commands
'''
from django.core.management.base import BaseCommand
from optparse import make_option

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Handle javascript operations'

    def handle(self, *args, **options):
        pass
