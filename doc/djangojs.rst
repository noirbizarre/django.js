Django javascript module
========================

Reverse URLs
------------

The Django.js library expose reverse URLs to javascript.
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

You can use anonymous forms (variable arguments and array) with named arguments in URLs but you can't use object form with anonymous arguments.


Static URLs
-----------

You can obtain a static file url with:

.. code-block:: javascript

    Django.file('my-data.json');
    Django.file('another/data.pdf');


Constants
---------

Django.js wraps some Django constants:

- ``Django.STATIC_URL``
- ``Django.LANGUAGES``
- ``Django.LANGUAGE_CODE``
- ``Django.LANGUAGE_NAME``
- ``Django.LANGUAGE_NAME_LOCAL``
- ``Django.LANGUAGE_BIDI``
