Settings
========

You can tune a little ``Django.js`` behaviour using settings.
Django.js provide the following optionnal settings:


``JS_URLS_NAMESPACES``
----------------------

Serialized namespaces whitelist. If this setting is specified, only URLs from namespaces listed in will be serialized.


``JS_URLS_NAMESPACES_EXCLUDE``
------------------------------

Serialized namespaces blacklist. It this setting is specified, URLs from namespaces listed in will not be serialized.


``JS_I18N``
-----------

Serialized translations whitelist. If specified, only apps listed in will appear in the javascript translation catalog.


``JS_I18N_EXCLUDE``
-------------------

Serialized translations blacklist. If specified, apps listed in will not appear in the javascript translation catalog.
