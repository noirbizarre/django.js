Django.JS
=========

.. image:: https://secure.travis-ci.org/noirbizarre/django-js.png
   :target: http://travis-ci.org/noirbizarre/django-js

Django.JS provides helpers to bridge JavaScript developpement to Django.

Django.JS is inspired from:
 - `Miguel Araujo's verbatim snippet <https://gist.github.com/893408>`_.
 - `Dimitri Gnidash's django-js-utils <https://github.com/Dimitri-Gnidash/django-js-utils>`_.

Installation
------------

You can install Django.JS with pip::

    pip install django-js

or with easy_install::

    easy_install django-js


Add ``djangojs`` to your ``settings.INSTALLED_APPS``.

Add ``djangojs.urls`` to your root ``URL_CONF``::

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

- load the template tag lib into each template manually::

    {% load js %}

- load the template tag lib by adding to your ``setting.py``::

    from django.template import add_to_builtins

    add_to_builtins('djangojs.templatetags.js')


Usage
*****

verbatim
~~~~~~~~

A ``{% verbatim %}`` tag is available to ease the JS templating.
It escape a specific part. For example, you may want a subpart of your template to be rendered by Django ::

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
After loading, you can use the Django module to resolve URLs and Translations::

    {% django_js %}
    <script>
        console.log(
            Django.url('my-view'),
            Django.url('my-view', 'arg1'),
            Django.url('my-view', ['arg1']),
            Django.url('my-view', {key: 'test'}),
            Django.trans('my string')
        );
    </script>

``django_js`` tag also configure ``jQuery.ajax`` to handle CRSF tokens.


jquery_js
~~~~~~~~~

The ``{% jquery_js %}`` tag only load the jQuery (1.8.2) library.

The ``django_js`` tag automatically load jQuery so no need to manually load it.


js_lib
~~~~~~

The ``js_lib`` tag is a quick helper to include javascript files from ``{{STATIC_URL}}js/libs``::

    {% js_lib my-lib.js %}

is equivalent to::

    <script type="text/javascript" src="{{STATIC_URL}}js/libs/my-lib.js"></script>
