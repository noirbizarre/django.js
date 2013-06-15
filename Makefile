BASEDIR=$(CURDIR)
DOCDIR=$(BASEDIR)/doc
DISTDIR=$(BASEDIR)/dist
PACKAGE='djangojs'

help:
	@echo 'Makefile for Django.js                                               '
	@echo '                                                                     '
	@echo 'Usage:                                                               '
	@echo '   make serve            Run the test server                         '
	@echo '   make test             Run the test suite                          '
	@echo '   make doc              Generate the documentation                  '
	@echo '   make dist             Generate a distributable package            '
	@echo '   make release          Bump a version and publish it on PyPI       '
	@echo '   make clean            Remove all temporary and generated artifacts'
	@echo '                                                                     '


serve:
	@echo 'Running test server'
	@python manage.py runserver

test:
	@echo 'Running test suite'
	@python manage.py test djangojs

doc:
	@echo 'Generating documentation'
	@cd $(DOCDIR) && make html
	@echo 'Done'

dist:
	@echo 'Generating a distributable python package'
	@python setup.py sdist
	@echo 'Done'

release:
	@echo 'Bumping version and publishing it'
	@./release.sh
	@echo 'Done'

clean:
	rm -fr $(DISTDIR)

.PHONY: doc help clean test dist release
