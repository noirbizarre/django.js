#!/bin/bash

VENV=venv

if [ -d "$VENV" ]; then
    echo "-- activating virtualenv"
else
    echo "-- creating virtualenv"
    virtualenv --distribute -p python2.7 $VENV
fi
source $VENV/bin/activate
pip install -q -r requirements/jenkins.pip

python manage.py jenkins --pep8-ignore E127,E128,E261,E501
