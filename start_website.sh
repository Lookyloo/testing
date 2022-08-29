#!/usr/bin/env bash

set -e
set -x

export LOOKYLOO_TESTING_HOME=`pwd`
export FLASK_APP=__init__.py
cd website
flask run --host=0.0.0.0
cd ..
