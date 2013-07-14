Settings
========

You can tune Django.js behaviour using settings.
Django.js provide the following optionnal settings:

Libraries versions
~~~~~~~~~~~~~~~~~~

You can specify some libraries versions used by Django.js.


``JQUERY_VERSION``
------------------

Specify the jQuery version to use. If not specififed, default to last version.

Django.js provide the following versions:

- 2.0.3
- 2.0.2
- 2.0.1
- 2.0.0
- 1.10.2
- 1.10.1
- 1.9.1
- 1.9.0
- 1.8.3


URLs handling
~~~~~~~~~~~~~

Theses settings allow you to customize or disable Django.js URLs handling.

``JS_URLS_ENABLED``
-------------------

**Default:** ``True``

You can disable Django.js URLs handling by setting it to ``False``


``JS_URLS``
-----------

**Default:** ``None``

Serialized URLs names whitelist. If this setting is specified, only named URLs listed in will be serialized.


``JS_URLS_EXCLUDE``
------------------------------

**Default:** ``None``

Serialized URLs names blacklist. It this setting is specified, named URLs listed in will not be serialized.


``JS_URLS_NAMESPACES``
----------------------

**Default:** ``None``

Serialized namespaces whitelist. If this setting is specified, only URLs from namespaces listed in will be serialized.


``JS_URLS_NAMESPACES_EXCLUDE``
------------------------------

**Default:** ``None``

Serialized namespaces blacklist.
If this setting is specified, URLs from namespaces listed in will not be serialized.


``JS_URLS_UNNAMED``
-------------------

**Default:** ``False``

Serialize unnamed URLs. If this setting is set to ``True``,
unnamed URLs will be serialized (only for function based views).


Context handling
~~~~~~~~~~~~~~~~

Theses settings allow you to customize or disable Django.js context handling.

``JS_CONTEXT_ENABLED``
----------------------

**default:** ``True``

You can disable Django.js context handling by setting it to ``False``


``JS_CONTEXT``
--------------

**default:** ``None``

Serialized context variables names whitelist.
If this setting is specified, only context variables listed in will be serialized.

.. note:: ``LANGUAGE_NAME`` and ``LANGUAGE_NAME_LOCAL`` requires ``LANGUAGE_CODE`` to be also included.


``JS_CONTEXT_EXCLUDE``
----------------------

**Default:** ``None``

Serialized context variables names blacklist.
If this setting is specified, context variables names listed in will not be serialized.

.. note:: Excluding ``LANGUAGE_CODE`` also exclude ``LANGUAGE_NAME`` and ``LANGUAGE_NAME_LOCAL``.


.. _js-context-processor:

``JS_CONTEXT_PROCESSOR``
------------------------

**Default:** ``djangojs.utils.ContextSerializer``

Change this value if you want to specify a custom context serializer class.
The custom class must inherits from :class:`ContextSerializer <djangojs.utils.ContextSerializer>`


User handling
~~~~~~~~~~~~~

``JS_USER_ENABLED``
----------------------

**default:** ``True``

You can disable Django.js user handling by setting it to ``False``


Localization and internationalization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``JS_I18N_APPS``
----------------

**Default:** ``None``

Serialized translations whitelist.
If specified, only apps listed in will appear in the javascript translation catalog.


``JS_I18N_APPS_EXCLUDE``
------------------------

**Default:** ``None``

Serialized translations blacklist.
If specified, apps listed in will not appear in the javascript translation catalog.


.. _settings-i18n-patterns:

``JS_I18N_PATTERNS``
--------------------

**Default:** ``tuple()``

Custom patterns for localization using the :ref:`localize management command <command-localize>`.
Each entry should be a tuple ``(extension, dirname, pattern)`` where:

extension
    is an file extension to match

dirname
    is the application relative path to search into

pattern
    is a expressions to extract localizable strings (can be a list of regular expressions).


**Exemple:**

.. code-block:: python

    JS_I18N_PATTERNS = (
        ('hbs', 'static/templates', r'{{#trans}}(.*?){{/trans}}'),
    )


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

    # Disable user serialization
    JS_USER_ENABLED = False

    # Custom Context serializer
    JS_CONTEXT_PROCESSOR = 'my.custom.ContextProcessor'
