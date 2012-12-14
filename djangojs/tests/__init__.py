# -*- coding: utf-8 -*-
# pylint: disable=W0401
from .test_context import *
from .test_globber import *
from .test_javascript import *
from .test_settings import *
from .test_tags import *
from .test_tap import *
from .test_urls import *
# pylint: enable=W0401


def custom_processor(_):
    '''
    Custom template conext processor for testing purposes.
    '''
    return {'CUSTOM': 'CUSTOM_VALUE'}
