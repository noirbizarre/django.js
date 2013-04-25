RequireJS integration
=====================

Django.js works with `RequireJS`_ but it requires some extras step to do it.

Preloading prerequisites
------------------------

You should use the ``django_js_init`` template tag before loading your application with `RequireJS`_.

.. code-block:: html+django

    {% load js %}
    {% django_js_init %}
    <script data-main="scripts/main" src="scripts/require.js"></script>

It works with `django-require`_ too:

.. code-block:: html+django

    {% load js require %}
    {% django_js_init %}
    {% require_module 'main' %}


See :ref:`django-js-init-templatetag`.

shim configuration
------------------

You should add an extra shim configuration for Django.js:

.. code-block:: javascript

    require.config({
        paths: {
            django: 'djangojs/django'
        },

        shim: {
            "django": {
                "deps": ["jquery"],
                "exports": "Django"
            }
        }
    });


.. _RequireJS: http://requirejs.org/
.. _django-require: https://github.com/etianen/django-require
