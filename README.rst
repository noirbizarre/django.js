=========
Django.js
=========

.. image:: https://secure.travis-ci.org/noirbizarre/django.js.png
    :target: http://travis-ci.org/noirbizarre/django.js
.. image:: https://coveralls.io/repos/noirbizarre/django.js/badge.png?branch=master
    :target: https://coveralls.io/r/noirbizarre/django.js
.. image:: https://pypip.in/v/django.js/badge.png
    :target: https://crate.io/packages/django.js
.. image:: https://pypip.in/d/django.js/badge.png
    :target: https://crate.io/packages/django.js

Django.js provides tools for JavaScript development with Django.

Django.js is inspired from:

- `Miguel Araujo's verbatim snippet <https://gist.github.com/893408>`_.
- `Dimitri Gnidash's django-js-utils <https://github.com/Dimitri-Gnidash/django-js-utils>`_.

This is currently a work in progress (API wil not be stable before 1.0) so don't expect it to be perfect but please `submit an issue <https://github.com/noirbizarre/django.js/issues>`_ for any bug you find or any feature you want.

Compatibility
=============

Django.js requires Python 2.6+ and Django 1.4.2+.


Installation
============

You can install Django.js with pip:

.. code-block:: console

    $ pip install django.js

or with easy_install:

.. code-block:: console

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

The documentation is hosted `on Read the Docs <http://djangojs.readthedocs.org/en/latest/>`_
