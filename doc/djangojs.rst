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

You can use anonymous forms (variable arguments and array) with named arguments in urls but you can't use object form with anonymous arguments.

ready event
***********

Django.js needs to load 2 JSON files before being ready:

- one containing every urls needed for reverse matching.
- another one containing all context data like ``STATIC_URL`` or ``LANGUAGE``.

It emits a ``ready`` event when fetch is done.
If you need to have use the ``Django`` module as soon as possible, you can listen to this event:

.. code-block:: javascript

    $(Django).on('ready', function() {
        console.log(
            Django.url('my-view')
        );
    });


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
