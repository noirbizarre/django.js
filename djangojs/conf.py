# -*- coding: utf-8 -*-
import sys

from django.test.signals import setting_changed
from django.dispatch import receiver

# Default configuration values for Django.js
# All values used by Django.js needs to appears here.
DEFAULTS = {
    'DEBUG': True,
    'TESTING': 'test' in sys.argv,
    'JS_URLS': None,
    'JS_URLS_EXCLUDE': None,
    'JS_URLS_NAMESPACES': None,
    'JS_URLS_NAMESPACES_EXCLUDE': None,
    'JS_I18N_APPS': None,
    'JS_I18N_APPS_EXCLUDE': None,
}

# All required settings keys to import rom project
REQUIREDS = (
    'INSTALLED_APPS',
    'STATIC_URL',
    'ROOT_URLCONF',
)


class Settings(dict):
    '''
    Django settings wrapper
    '''

    def __init__(self):
        """
        Try and initialize with Django settings.
        All values from DEFAULTS will be overwritten by project settings if present.
        """
        try:
            from django.conf import settings

            self.update(DEFAULTS)
            self.update(settings._wrapped.__dict__)

            # Warn for missings settings
            for key in REQUIREDS:
                if not key in self:
                    raise Exception('%s settings key is mandatory' % key)

        except ImportError:
            pass

    def __getattr__(self, k):
        return self[k]


settings = Settings()


@receiver(setting_changed)
def on_settings_changed(sender, **kwargs):
    key, value = kwargs['setting'], kwargs['value']
    settings[key] = value
