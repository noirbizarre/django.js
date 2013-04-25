Integration with other Django apps
==================================

Django Absolute
---------------

`Django Absolute`_ contribute with the following context variables:

- ``ABSOLUTE_ROOT``
- ``ABSOLUTE_ROOT_URL``
- ``SITE_ROOT``
- ``SITE_ROOT_URL``

They will be available into ``Django.context`` javascript object (nothing new, this the default behavior).
But, two more methods will be available:

- ``Django.absolute()`` to reverse an absolute URL based on request
- ``Django.site()`` to reverse an absolute URL based on Django site

If you try to call these methods without django-bsolute installed, a ``DjangoJsError`` will be thrown.


.. _django-pipeline:

Django Pipeline
---------------

If you want to compress Django.js with `Django Pipeline`_, you should change the way you load django.js.

First add jQuery and Django.js to your pipelines in you ``settings.py``:

.. code-block:: python

    PIPELINE_JS = {
        'base': {
            'source_filenames': (
                '...',
                'js/libs/jquery-1.9.1.min.js',
                'js/djangojs/django.js',
                '...',
            ),
            'output_filename': 'js/base.min.js',
        },
    }


Instead of using the ``django_js`` template tag:

.. code-block:: html+django

    {% load js %}
    {% django_js %}

you should use the :ref:`django_js_init <django-js-init-templatetag>` and include your compressed bundle:

.. code-block:: html+django

    {% load js compressed %}
    {% django_js_init %}
    {% compressed_js "base" %}


.. _`Django Absolute`: https://github.com/noirbizarre/django-absolute
.. _`Django Pipeline`: https://github.com/cyberdelia/django-pipeline
