Management Commands
===================

Django.js provide a management command to simplify some common JavaScript tasks:

.. code-block:: console

    $ python manage.py js -h
    usage: manage.py js [-h] [-v {0,1,2,3}] [--settings SETTINGS]
                        [--pythonpath PYTHONPATH] [--traceback]
                        {bower,launcher,localize} ...

    Handle javascript operations

    optional arguments:
      -h, --help            show this help message and exit
      -v {0,1,2,3}, --verbosity {0,1,2,3}
                            Verbosity level; 0=minimal output, 1=normal output,
                            2=verbose output, 3=very verbose output
      --settings SETTINGS   The Python path to a settings module, e.g.
                            "myproject.settings.main". If this isn't provided, the
                            DJANGO_SETTINGS_MODULE environment variable will be
                            used.
      --pythonpath PYTHONPATH
                            A directory to add to the Python path, e.g.
                            "/home/djangoprojects/myproject".
      --traceback           Print traceback on exception

    subcommands:
      JavaScript command to execute

      {bower,launcher,localize}
        bower               Generate a .bowerrc file
        launcher            Get a PhantomJS launcher path
        localize            Generate PO file from js files


.. _command-localize:

``localize``
------------

The ``localize`` command generates a ``.po`` file for your javascript files.
It allows you to localize your templates with custom patterns.

Custom patterns are specified in :ref:`settings.JS_I18N_PATTERNS <settings-i18n-patterns>`.

Let says you use `Handlebars`_ as client-side template engine,
all your templates are ``.hbs`` files in your app ``static/templates`` directory
and you registered a ``trans`` helper to handle localization:

.. code-block:: javascript

    Handlebars.registerHelper('trans', function(opt) {
        return gettext(opt.fn(this));
    });

So, in your handlebars templates, you will have some localizable strings like:

.. code-block:: html+jinja

    {{#trans}}my translatable label{{/trans}}

You can add this to your ``settings.py`` file to extract localizable strings
from them:

.. code-block:: python

    JS_I18N_PATTERNS = (
        ('hbs', 'static/templates', r'{{#trans}}(.*?){{/trans}}'),
    )

Running the localize command:

.. code-block:: console

    $ python manage.py js localize -l fr

will extract all localizable strings from your ``.js`` files as usual and add those in your ``.hbs`` files.

.. code-block:: console

    $ python manage.py js localize -h
    usage: manage.py js localize [-h] [--locale LOCALE] [--all]
                                   [--extension EXTENSIONS] [--symlinks]
                                   [--ignore PATTERN] [--no-default-ignore]
                                   [--no-wrap] [--no-location] [--no-obsolete]
                                   [app [app ...]]

    Generate PO file from js files

    positional arguments:
      app                   Applications to localize

    optional arguments:
      -h, --help            show this help message and exit
      --locale LOCALE, -l LOCALE
                            Creates or updates the message files for the given
                            locale (e.g. pt_BR).
      --all, -a             Updates the message files for all existing locales.
      --extension EXTENSIONS, -e EXTENSIONS
                            The file extension(s) to examine (default: "js").
                            Separate multiple extensions with commas, or use -e
                            multiple times.
      --symlinks, -s        Follows symlinks to directories when examining source
                            code and templates for translation strings.
      --ignore PATTERN, -i PATTERN
                            Ignore files or directories matching this glob-style
                            pattern. Use multiple times to ignore more.
      --no-default-ignore   Don't ignore the common glob-style patterns 'CVS',
                            '.*' and '*~'.
      --no-wrap             Don't break long message lines into several lines
      --no-location         Don't write '#: filename:line' lines
      --no-obsolete         Remove obsolete message strings


``bower``
---------

The ``bower`` command generates a ``.bowerrc`` file into the current directory
specifying the target directory for `Bower`_ downloads.

.. code-block:: console

    $ python manage.py js bower -h
    usage: manage.py js bower [-h] [-f] target

    Generate a .bowerrc file

    positional arguments:
      target       The target directory for bower downloads

    optional arguments:
      -h, --help   show this help message and exit
      -f, --force  Overwrite the file if exists


**exemple:**

.. code-block:: console

    $ python manage.py js bower myproject/static/bower
    Created .bowerrc file into the current directory
    $ cat .bowerrc
    {"directory": "./myproject/static/bower/"}


``launcher``
------------

The ``launcher`` command returns the full path to a Django.js PhantomJS runner
(usefull if you need to execute it manually).

.. code-block:: console

    $ python manage.py js launcher -h
    usage: manage.py js launcher [-h] name

    Get a PhantomJS launcher path

    positional arguments:
      name        Runner name

    optional arguments:
      -h, --help  show this help message and exit


**exemple:**

.. code-block:: console

    $ python manage.py js launcher jasmine
    /var/lib/python2.7/site-packages/django.js/djangojs/phantomjs/jasmine-runner.js


.. _Handlebars: http://handlebarsjs.com
.. _Bower: http://bower.io
