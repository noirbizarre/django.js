=========
Django.js
=========

.. image:: https://secure.travis-ci.org/noirbizarre/django.js.png
   :target: http://travis-ci.org/noirbizarre/django.js

Django.js provides tools for JavaScript development with Django.

Django.js is inspired from:

- `Miguel Araujo's verbatim snippet <https://gist.github.com/893408>`_.
- `Dimitri Gnidash's django-js-utils <https://github.com/Dimitri-Gnidash/django-js-utils>`_.

This is currently a work in progress (API wil not be stable before 1.0) so don't expect it to be perfect but please `submit an issue <https://github.com/noirbizarre/django.js/issues>`_ for any bug you find or any feature you want.


Installation
============

You can install Django.JS with pip:

.. code-block:: bash

    $ pip install django.js

or with easy_install:

.. code-block:: bash

    $ easy_install django.js


Add ``djangojs`` to your ``settings.INSTALLED_APPS``.

Add ``djangojs.urls`` to your root ``URL_CONF``:

.. code-block:: python

    urlpatterns = patterns('',
        ...
        url(r'^djangojs/', include('djangojs.urls')),
        ...
    )


Documentation
=============

The documentation is hosted `on Read the Docs <http://djangojs.readthedocs.org/en/0.3.2/>`_
