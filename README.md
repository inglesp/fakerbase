# Fakerbase

[![Build Status](https://travis-ci.org/inglesp/fakerbase.svg?branch=master)](https://travis-ci.org/inglesp/fakerbase)
[![Code Health](https://landscape.io/github/inglesp/fakerbase/master/landscape.svg)](https://landscape.io/github/inglesp/fakerbase/master)

Speed up your Django test suite with Fakerbase!

Rather than converting each database request to SQL, sending it to the
database, and parsing the response, Fakerbase intercepts certain functions in
the ORM, and queries its own in-memory Python database.


### How do I use it?

You'll need to have a separate settings file for running tests with Fakerbase.
In this settings file, add `fakerbase` to `INSTALLED_APPS`.  Now, whenever you
use these settings to run any tests that use `django.test.TestCase`, Fakerbase
will intercept calls to the database, and (hopefully) provide you with tests
that have an airspeed velocity approaching that of an unladen swallow.


### What can Fakerbase do?

Right now, not a lot!  But the plan is for it to be able to handle any database
request that could be generated by the ORM.


### Which versions of Django are supported?

Currently, only Django 1.7.1 is supported, but wider support is planned.


### Developing

* Create a virtualenv and install requirements with `pip install -r
  requirements-dev`
* Run tests with `./manage.py test`

