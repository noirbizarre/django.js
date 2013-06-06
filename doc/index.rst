.. django.js documentation master file, created by
   sphinx-quickstart on Fri Oct  5 09:50:20 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to django.js documentation!
===================================

Django.js provides tools for JavaScript development with Django.

Django.js is inspired from:

- `Miguel Araujo's verbatim snippet <https://gist.github.com/893408>`_.
- `Dimitri Gnidash's django-js-utils <https://github.com/Dimitri-Gnidash/django-js-utils>`_.

.. note::
    This is currently a work in progress (API wil not be stable before 1.0) so don't expect it to be perfect but please `submit an issue <https://github.com/noirbizarre/django.js/issues>`_ for any bug you find or any feature you want.


Compatibility
=============

Django.js requires Python 2.6+ and Django 1.4.2+.


Installation
============

You can install Django.js with pip:

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

.. toctree::
    :maxdepth: 2

    templatetags
    djangojs
    requirejs
    test
    integration
    settings
    api
    changelog


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

