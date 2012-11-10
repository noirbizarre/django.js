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

.. _`Django Absolute`: https://github.com/noirbizarre/django-absolute
