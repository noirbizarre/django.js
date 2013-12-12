# -*- coding: utf-8 -*-
'''
This modules holds every helpers that does not fit in any standard django modules.
'''
from __future__ import unicode_literals

import logging
import os
import sys

from django.contrib.staticfiles import finders
from django.contrib.staticfiles.utils import matches_patterns
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import force_text
from django.utils.functional import Promise

logger = logging.getLogger(__name__)


__all__ = (
    'class_from_string',
    'LazyJsonEncoder',
    'StorageGlobber',
)


def class_from_string(name):
    '''
    Get a python class object from its name
    '''
    module_name, class_name = name.rsplit('.', 1)
    __import__(module_name)
    module = sys.modules[module_name]
    return getattr(module, class_name)


class LazyJsonEncoder(DjangoJSONEncoder):
    '''
    A JSON encoder handling promises (aka. Django lazy objects).

    See: https://docs.djangoproject.com/en/dev/topics/serialization/#id2
    '''
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super(LazyJsonEncoder, self).default(obj)


class StorageGlobber(object):
    '''
    Retrieve file list from static file storages.
    '''
    @classmethod
    def glob(cls, files=None):
        '''
        Glob a pattern or a list of pattern static storage relative(s).
        '''
        files = files or []
        if isinstance(files, str):
            files = os.path.normpath(files)
            matches = lambda path: matches_patterns(path, [files])
            return [path for path in cls.get_static_files() if matches(path)]
        elif isinstance(files, (list, tuple)):
            all_files = cls.get_static_files()
            files = [os.path.normpath(f) for f in files]
            sorted_result = []
            for pattern in files:
                sorted_result.extend([f for f in all_files if matches_patterns(f, [pattern])])
            return sorted_result

    @classmethod
    def get_static_files(cls):
        files = []
        for finder in finders.get_finders():
            for path, storage in finder.list(None):
                # Prefix the relative path if the source storage contains it
                if getattr(storage, 'prefix', None):
                    prefixed_path = os.path.join(storage.prefix, path)
                else:
                    prefixed_path = path

                if prefixed_path not in files:
                    files.append(os.path.normpath(prefixed_path))
        return files
