# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def booleans(request):
    '''
    Allow to use booleans in templates.

    See: http://stackoverflow.com/questions/4557114/django-custom-template-tag-which-accepts-a-boolean-parameter
    '''
    return {
        'True': True,
        'true': True,
        'False': False,
        'false': False,
    }
