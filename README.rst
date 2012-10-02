Django.js
=========

.. image:: https://secure.travis-ci.org/noirbizarre/django.js.png
   :target: http://travis-ci.org/noirbizarre/django.js

Django.js provides tools for JavaScript development with Django.

This is currently a work in progress so don't expect it to be perfect.

Django.js is inspired from:
 - `Miguel Araujo's verbatim snippet <https://gist.github.com/893408>`_.
 - `Dimitri Gnidash's django-js-utils <https://github.com/Dimitri-Gnidash/django-js-utils>`_.

Installation
------------

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


Template tags
-------------

Initialization
**************
You can either:

- load the template tag lib into each template manually:

.. code-block:: html+django

    {% load js %}

- load the template tag lib by adding to your ``setting.py``:

.. code-block:: python

    from django.template import add_to_builtins

    add_to_builtins('djangojs.templatetags.js')


Usage
*****

verbatim
~~~~~~~~

A ``{% verbatim %}`` tag is available to ease the JS templating.
It escape a specific part. For example, you may want a subpart of your template to be rendered by Django :

.. code-block:: html+django

    <script type="text/x-handlebars" id="tpl-django-form">
        <form>
            {% verbatim %}
                {{#if id}}<h1>{{ id }}</h1>{{/if}}
            {% endverbatim %}
            {{ yourform.as_p }}
        </form>
    </script>



django_js
~~~~~~~~~

A ``{% django_js %}`` tag is available to provide the Django JS module.
After loading, you can use the Django module to resolve URLs and Translations:

.. code-block:: html+django

    {% django_js %}
    <script>
        $(Django).on('ready', function() {
            console.log(
                Django.url('my-view'),
                Django.url('my-view', 'arg1'),
                Django.url('my-view', ['arg1']),
                Django.url('my-view', {key: 'test'}),
                Django.trans('my string')
            );
        });
        Django.init({% django_urls_json %});
    </script>


If you don't want to manually trigger initialization, you can use the ``{% django_js_init %}`` tag:

.. code-block:: html+django

    {% django_js_init %}
    <script>
        $(Django).on('ready', function() {
            console.log(Django.url('my-view'));
        });
    </script>

``django_js`` tag also configure ``jQuery.ajax`` to handle CSRF tokens.


jquery_js
~~~~~~~~~

The ``{% jquery_js %}`` tag only load the jQuery (1.8.2) library.

The ``django_js`` and ``django_js_init`` tags automatically load jQuery so no need to manually load it.


js_lib
~~~~~~

The ``js_lib`` tag is a quick helper to include javascript files from ``{{STATIC_URL}}js/libs``:

.. code-block:: html+django

    {% js_lib "my-lib.js" %}

is equivalent to:

.. code-block:: html+django

    <script type="text/javascript" src="{{STATIC_URL}}js/libs/my-lib.js"></script>


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


Constants
---------

Django.js wraps some Django constants:

- ``Django.STATIC_URL``
- ``Django.LANGUAGES``
- ``Django.LANGUAGE_CODE``
- ``Django.LANGUAGE_NAME``
- ``Django.LANGUAGE_NAME_LOCAL``
- ``Django.LANGUAGE_BIDI``


Other features
--------------

When the ``django_js`` template tag is included in a page, it automatically:

- Patch ``jQuery.ajax()`` to handle CSRF tokens
- loads the django javascript catalog for all apps supporting it
- loads the django javascript i18n/l10n tools in the page:
   - ``gettext()``
   - ``ngettext()``
   - ``interpolate()``
