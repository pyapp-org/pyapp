######################################
pyApp - A python application framework
######################################

*Let us handle the boring stuff!*

.. image:: https://img.shields.io/travis/timsavage/pyapp.svg?style=flat
   :target: https://travis-ci.org/timsavage/pyapp
   :alt: Travis CI Status

.. image:: https://codecov.io/gh/timsavage/pyapp/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/timsavage/pyapp
   :alt: Test Coverage

.. image:: https://landscape.io/github/timsavage/pyapp/master/landscape.svg?style=flat
   :target: https://landscape.io/github/timsavage/pyapp/master
   :alt: Code Health

Many features inspired by Django, but modified to be more general for use outside of web applications.

The development philosophy for this library is Python 3 first, with features
back ported to Python 2.7 where possible.

So what do we handle?
=====================

- Configuration - Loading, merging your settings from different sources (Python, JSON)
- Instance Factories - Configuration of plugins, database connections, or just implimentations from of an ``ABC``. Leveraging settings to make setup of your application easy and reduce coupling.
- Checks - A framework for checking your settings are correct, can the application connect to that API end point?
- Application - Provides a extensible and simple CLI interface for adding more commands, comes with commands to support Checks, settings.

Coming soon
-----------

Support for common services eg email, as well as companion libraries to add plugin factories for SQL Alchemy, Redis, Paramiko, LDAP etc.
