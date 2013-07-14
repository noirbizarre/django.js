Contributing
============

Django.js is open-source and very open to contributions.

Submitting issues
-----------------

Issues are contributions in a way so don't hesitate
to submit reports on the `official bugtracker`_.

Provide as much informations as possible to specify the issues:

- the Django.js version used
- a stacktrace
- installed applications list
- ...


Submitting patches (bugfix, features, ...)
------------------------------------------

If you want to contribute some code:

1. fork the `official Django.js repository`_
2. create a branch with an explicit name (like ``my-new-feature`` or ``issue-XX``)
3. do your work in it
4. rebase it on the master branch from the official repository (cleanup your history by performing an interactive rebase)
5. submit your pull-request

There are some rules to follow:

- your contribution should be documented (if needed)
- your contribution should be tested and the test suite should pass successfully
- your code should be mostly PEP8 compatible with a 120 characters line length
- your contribution should support both Python 2 and 3 (use ``tox`` to test)


A Makefile is provided to simplify the common tasks:

.. code-block:: console

    $ make
    Makefile for Django.js

    Usage:
       make serve            Run the test server
       make test             Run the test suite
       make pep8             Run the PEP8 report
       make doc              Generate the documentation
       make dist             Generate a distributable package
       make minify           Minify Django.js with yuglify
       make release          Bump a version and publish it on PyPI
       make clean            Remove all temporary and generated artifacts


To ensure everything is fine before submission, use ``tox``.
It will run the test suite on all the supported Python version
and ensure the documentation is generating.

.. code-block:: console

    $ pip install tox
    $ tox


**Don't forget client-side code and tests.**

You can run the javascript test suite in the browser (http://localhost:8000).
Javascript tests are run in the test suite too, but it runs on the minified version of the javascript libary.

You can either minify it manually by running the provided script

.. code-block:: console

    $ ./minify.sh
    $ python manage.py test djangojs

or use the Makefile ``minify`` task that minify the javascript:

.. code-block:: console

    $ make minify test

.. note::

    minification use ``yuglify`` so you need to install it before: ``npm install -g yuglify``


.. _official Django.js repository: https://github.com/noirbizarre/django.js
.. _official bugtracker: https://github.com/noirbizarre/django.js/issues
