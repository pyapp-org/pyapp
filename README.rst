######################################
pyApp - A python application framework
######################################

*Let us handle the boring stuff!*

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/ambv/black
   :alt: Once you go Black...

.. image:: https://img.shields.io/travis/timsavage/pyapp.svg?style=flat
   :target: https://travis-ci.org/timsavage/pyapp
   :alt: Travis CI Status

.. image:: https://codecov.io/gh/timsavage/pyapp/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/timsavage/pyapp
   :alt: Test Coverage


Many features inspired by Django, but modified to be more general for use outside of web applications.

PyApp wit the release of 4.0 supports Python 3.6+ all previous versions are no longer supported.
This change allows for the user of F-Strings, and removal of any compatibility code.

So what do we handle?
=====================

- Configuration - Loading, merging your settings from different sources
  + Python modules
  + Files and HTTP(s) endpoints for JSON and YAML files.
- Instance Factories - Configuration of plugins, database connections, or just implementations of an ``ABC``.
  Leveraging settings to make setup of your application easy and reduce coupling.
- Checks - A framework for checking your settings are correct, can the application connect to that API end point?
- Application - Provides a extensible and simple CLI interface for adding more commands, comes with commands to support Checks, settings.

Coming soon
-----------

Support for common services eg email, as well as companion libraries to add plugin factories for SQL Alchemy, Redis, Paramiko, LDAP etc.
