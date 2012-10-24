Javascript test tools
=====================

Django.js provide tools for easy javascript testing.

Views
-----
Django.js provides base views for javascript testing.
Instead of writing a full view each time you need a Jasmine or a QUnit test view, simply use the provided ``JasmineView`` and ``QUnitView`` and add them to your test_urls.py:


.. code-block:: python

    from django.conf.urls import patterns, url, include

    from djangojs.views import JasmineView, QUnitView


    class JasmineTestView(JasmineView):
        js_files = 'js/test/*.specs.js'

    class QUnitTestView(QUnitView):
        js_files = 'js/test/*.test.js'

    urlpatterns = patterns('',
        url(r'^jasmine$', JasmineTestView.as_view(), name='my_jasmine_view'),
        url(r'^qunit$', QUnitTestView.as_view(), name='my_qunit_view'),
    )

These views extends the Django TemplateView so you can add extra context entries and you can customize the template by extending them.

You can inspect django.js own test suites on github.

Test cases
----------

A Phantom.js test runner is provided with Jasmine/QUnit support.
To use it with the previously defined views, just call the ``run_jasmine()`` or ``run_qunit()`` methods:

.. code-block:: python

    class JsTests(JsTestCase):
        urls = 'myapp.test_urls'

        def test_jasmine_suite(self):
            '''It should run its its own Jasmine test suite'''
            self.run_jasmine('my_jasmine_view', title='Jasmine Test Suite')

        def test_qunit_suite(self):
            '''It should run its its own QUnit test suite'''
            self.run_qunit('my_qunit_view', title='QUnit Test Suite')

The verbosity is automatically adjusted with the ``-v/--verbosity`` parameter from the ``manage.py test`` command line.


.. warning::

    Phantom.js is required to use this feature and should be on your ``$PATH``.
