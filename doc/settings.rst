Settings
========

You can tune a little Django.js behaviour using settings.
Django.js provide the following optionnal settings:

``JQUERY_VERSION``
------------------

Specify the jQuery version to use. If not specififed, default to last version.

Django.js provide the following versions:

- 1.8.3
- 1.9.0
- 1.9.1
- 2.0.0


``JS_URLS``
-----------

Serialized URLs names whitelist. If this setting is specified, only named URLs listed in will be serialized.

- Default value: ``None``
- Expected: a list of URLs names to include only


``JS_URLS_EXCLUDE``
------------------------------

Serialized URLs names blacklist. It this setting is specified, named URLs listed in will not be serialized.

- Default value: ``None``
- Expected: a list of URLs names to exclude


``JS_URLS_NAMESPACES``
----------------------

Serialized namespaces whitelist. If this setting is specified, only URLs from namespaces listed in will be serialized.

- Default value: ``None``
- Expected: a list of URL namespaces to include only


``JS_URLS_NAMESPACES_EXCLUDE``
------------------------------

Serialized namespaces blacklist. It this setting is specified, URLs from namespaces listed in will not be serialized.

- Default value: ``None``
- Expected: a list of URL namespaces to exclude


``JS_URLS_UNNAMED``
-------------------

Serialize unnamed URLs. If this setting is set to ``True``,
unnamed URLs will be serialized (only for function based views).

- Default value: ``False``


``JS_I18N_APPS``
----------------

Serialized translations whitelist. If specified, only apps listed in will appear in the javascript translation catalog.

- Default value: ``None``
- Expected: a restricted application list to include in the javascript translation catalog


``JS_I18N_APPS_EXCLUDE``
------------------------

Serialized translations blacklist. If specified, apps listed in will not appear in the javascript translation catalog.

- Default value: ``None``
- Expected: an application list to exclude from the javascript translation catalog


Usage exemple
-------------

You could have, in your ``settings.py``:

.. code-block:: python

    # Exclude my secrets pages from serialized URLs
    JS_URLS_EXCLUDE = (
        'my_secret_page',
        'another_secret_page',
    )
    # Only include admin namespace
    JS_URLS_NAMESPACES = (
        'admin',
    )
    # Only include my apps' translations
    JS_I18N_APPS = ('myapp', 'myapp.other')
