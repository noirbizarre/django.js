# -*- coding: utf-8 -*-
import sys

# Default configuration values for Django.js
# All values used by Django.js needs to appears here.
DEFAULTS = {
    'DEBUG': True,
    'TESTING': 'test' in sys.argv,
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

            self.update(settings._wrapped.__dict__)

            # Warn for missings settings
            for key in REQUIREDS:
                if not key in self:
                    raise Exception('%s settings key is mandatory')

            # Set defaults for missing keys
            for key, value in DEFAULTS.iteritems():
                if not key in self:
                    self[key] = value

        except ImportError:
            pass

    # def set_max_message_length(self):
    #     extra_message_chars = "#PRIVMSG %s :\r\n" % self["IRC_CHANNEL"]
    #     self["MAX_MESSAGE_LENGTH"] = 512 - len(extra_message_chars)

    def __getattr__(self, k):
        return self[k]


settings = Settings()
