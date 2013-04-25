Template tags
=============

Initialization
--------------

You can either:

- load the template tag lib into each template manually:

.. code-block:: html+django

    {% load js %}

- load the template tag lib by adding to your ``views.py``:

.. code-block:: python

    from django.template import add_to_builtins

    add_to_builtins('djangojs.templatetags.js')


If you want to use boolean parameters, Django.js provide the ``djangojs.context_processors.booleans`` to help. Simply add it to your ``settings.CONTEXT_PROCESSORS``.
If not, you should use the string versions: ``param="True"``.


Usage
-----

django_js
~~~~~~~~~

A ``{% django_js %}`` tag is available to provide the Django JS module.
After loading, you can use the Django module to resolve URLs and Translations:

.. code-block:: html+django

    {% django_js %}
    <script>
        console.log(
            Django.url('my-view', {key: 'test'}),
            Django.file('test.json'),
            Django.context.STATIC_URL
        );
    </script>

It supports the following keyword parameters (in this order if you want to omit the keyword):

=========== ========= ======================================
 Parameter   Default                Description
=========== ========= ======================================
``jquery``  ``true``  Load the jQuery library
``i18n``    ``true``  Load the javascript i18n catalog
``csrf``    ``true``  Patch jQuery.ajax() fot Django CSRF
=========== ========= ======================================


You can disable all this features by simply providing arguments to the template tag:

.. code-block:: html+django

    {% django_js jquery=false i18n=false csrf=false %}


.. _django-js-init-templatetag:

django_js_init
~~~~~~~~~~~~~~

The ``{% django_js_init %}`` provide the necessary bootstrap for the Django.js without loading it.
It allows you to use Django.js with an AMD loader or a javascript compressor.
It supports the following keyword parameters (in this order if you want to omit the keyword):

=========== ========= ======================================
 Parameter   Default                Description
=========== ========= ======================================
``i18n``    ``true``  Load the javascript i18n catalog
``csrf``    ``true``  Patch jQuery.ajax() fot Django CSRF
=========== ========= ======================================


You can disable all this features by simply providing arguments to the template tag:

.. code-block:: html+django

    {% django_js_init i18n=false csrf=false %}


If you want to use it with require.js or Django Pipeline, see :doc:`requirejs` or :ref:`django-pipeline`.


Internationalization
********************

When the ``{% django_js %}`` template tag is included in a page, it automatically:

- loads the django javascript catalog for all supported apps
- loads the django javascript i18n/l10n tools in the page:
   - ``gettext()``
   - ``ngettext()``
   - ``interpolate()``

You can disable this feature by setting the ``i18n`` keyword parameter to ``false``.

.. note::

    You can filter included apps by using either the settings whitelist ``settings.JS_I18N`` or the settings blacklist ``settings.JS_I18N_EXCLUDE`` or both.
    For more informations, see :doc:`settings`.

jQuery Ajax CSRF
****************

When the ``django_js`` template tag is ininitialized it automatically patch ``jQuery.ajax()`` to handle CSRF tokens on ajax request.

You can disable this feature by setting the ``csrf`` keyword parameter to ``false``.

You can manually enable it later with:

.. code-block:: javascript

    Django.jquery_csrf();


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


.. note:: Starting from Django 1.5, use the included `verbatim tag <https://docs.djangoproject.com/en/dev/ref/templates/builtins/#std:templatetag-verbatim>`_ .

jquery_js
~~~~~~~~~

The ``{% jquery_js %}`` tag only load the jQuery library.

You can override the version either by passing the version as a parameter or setting the version with the ``settings.JQUERY_VERSION`` property.
For more informations, see :doc:`settings`.

You can optionnaly load the `jQuery Migrate <http://plugins.jquery.com/migrate/>`_ plugins for legacy support with jQuery 1.9.0+.

.. code-block:: html+django

    {% jquery_js %}
    {% jquery_js "1.8.3" %}
    {% jquery_js migrate=true %}


The ``django_js`` tag automatically load jQuery so no need to manually load it unless you set ``jquery=false``.


javascript/js
~~~~~~~~~~~~~

The ``javascript`` and ``js`` tags are the same quick helper to include javascript files from ``{{STATIC_URL}}``:

.. code-block:: html+django

    {% javascript "js/my.js" %}
    {% js "js/my.js" %}

is equivalent to:

.. code-block:: html+django

    <script type="text/javascript" src="{% static "js/my.js" %}"></script>

Both tags take an options ``type`` parameter that specifies the content type of the ``script`` tag:

.. code-block:: html+django

    {% javascript "js/my.coffee" type="text/coffeescript" %}

yields:

.. code-block:: html+django

    <script type="text/coffeescript" src="{% static "js/my.coffee" %}"></script>


css
~~~

The ``css`` tag is a quick helper to include css files from ``{{STATIC_URL}}``:

.. code-block:: html+django

    {% css "css/my.css" %}

is equivalent to:

.. code-block:: html+django

    <link rel="stylesheet" type="text/css" href="{% static "css/my.css" %}" />


js_lib
~~~~~~

The ``js_lib`` tag is a quick helper to include javascript files from ``{{STATIC_URL}}js/libs``:

.. code-block:: html+django

    {% js_lib "my-lib.js" %}

is equivalent to:

.. code-block:: html+django

    <script type="text/javascript" src="{{STATIC_URL}}js/libs/my-lib.js"></script>
