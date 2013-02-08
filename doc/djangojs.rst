Django javascript module
========================

Reverse URLs
------------

The Django.js library expose reverse urls to javascript.
You can call the ``Django.url()`` method with:

- an url name without arguments

.. code-block:: javascript

    Django.url('my-view');

- an url name and a variable number of arguments

.. code-block:: javascript

    Django.url('my-view', arg1, arg2);

- an url name and an array of arguments

.. code-block:: javascript

    Django.url('my-view' [arg1, arg2]);

- an url name and an object with named arguments

.. code-block:: javascript

    Django.url('my-view', {arg1: 'value1', arg2: 'value2'});

- an url name with one or more namespaces

.. code-block:: javascript

    Django.url('ns:my-view');
    Django.url('ns:nested:my-view');

You can use anonymous forms (variable arguments and array) with named arguments in urls but you can't use object form with anonymous arguments.

.. note::

    You can filter included urls names and namespaces by using either the settings whitelists and blacklists: ``settings.JS_URLS``, ``settings.JS_URLS_EXCLUDE``, ``settings.JS_URLS_NAMESPACES``, ``settings.JS_URLS_NAMESPACES_EXCLUDE``.
    For more informations, see :doc:`settings`.


Static URLs
-----------

You can obtain a static file url with:

.. code-block:: javascript

    Django.file('my-data.json');
    Django.file('another/data.pdf');


Context
-------

Django.js wraps some Django values normally accessible in the template context:

- ``Django.context.STATIC_URL``
- ``Django.context.MEDIA_URL``
- ``Django.context.LANGUAGES``
- ``Django.context.LANGUAGE_CODE``
- ``Django.context.LANGUAGE_NAME``
- ``Django.context.LANGUAGE_NAME_LOCAL``
- ``Django.context.LANGUAGE_BIDI``

In fact, any value contributed by a context processor and serializable will be accessible from ``Django.context``.

Permissions
-----------

Django.js allows you to check user permissions from client side. Simply call the ``Django.has_perm()`` method:

.. code-block:: javascript

    if (Django.has_perm('myapp.do_something')) {
        do_something();
    }
