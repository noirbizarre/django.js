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


Usage
-----

django_js
~~~~~~~~~

A ``{% django_js %}`` tag is available to provide the Django JS module.
After loading, you can use the Django module to resolve URLs and Translations:

.. code-block:: html+django

    {% django_js %}
    <script>
        $(Django).on('ready', function() {
            console.log(
                Django.url('my-view', {key: 'test'}),
                Django.file('test.json'),
                Django.context.STATIC_URL
            );
        });
    </script>


If you want to manually trigger initialization, you can set the ``init`` keyword to false:

.. code-block:: html+django

    {% django_js init=false %}
    <script>
        $(Django).on('ready', function() {
            console.log(
                Django.url('my-view')
            );
        });
        Django.init();
    </script>


The jQuery libary is automatically loaded.
If you want to manually load the jquery, you can set the ``jquery`` keyword to false:

.. code-block:: html+django

    {% django_js jquery=false %}


Internationalization
********************

When the ``{% django_js %}`` template tag is included in a page, it automatically:

- loads the django javascript catalog for all supported apps
- loads the django javascript i18n/l10n tools in the page:
   - ``gettext()``
   - ``ngettext()``
   - ``interpolate()``


jQuery Ajax CSRF
****************

When the ``django_js`` template tag is ininitialized it automatically patch ``jQuery.ajax()`` to handle CSRF tokens on ajax request.


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



jquery_js
~~~~~~~~~

The ``{% jquery_js %}`` tag only load the jQuery (1.8.2) library.

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

