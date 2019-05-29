######################################
pyApp - A python application framework
######################################

*Let us handle the boring stuff!*

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/ambv/black
   :alt: Once you go Black...

.. image:: https://img.shields.io/travis/pyapp-org/pyapp.svg?style=flat
   :target: https://travis-ci.org/pyapp-org/pyapp
   :alt: Travis CI Status

.. image:: https://codecov.io/gh/pyapp-org/pyapp/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/pyapp-org/pyapp
   :alt: Test Coverage

.. image:: https://api.codeclimate.com/v1/badges/58f9ffacb711c992610d/maintainability
   :target: https://codeclimate.com/github/pyapp-org/pyapp/maintainability
   :alt: Maintainability


Many features inspired by Django, but modified to be more general for use
outside of web applications.

With PyApp 4.0, support for versions of Python < 3.6 are no longer supported.


So what do we handle?
=====================

- Configuration - Loading, merging your settings from different sources
  + Python modules
  + File and HTTP(S) endpoints for JSON and YAML files.
- Instance Factories - Configuration of plugins, database connections, or just
  implementations of an ``ABC``.
  Leveraging settings to make setup of your application easy and reduce coupling.
- Checks - A framework for checking settings are correct and checking that your
  application connect to that API end point (your ops team will love you)?
- Extensions - Extend the basic framework with extensions, the framework provides
  deterministic startup and the ability to register checks and default settings.
- Application - Provides a extensible and simple CLI interface for starting
  running commands, comes with built-in commands to support Checks, report
  settings/extensions.
- Logging - Initialise and apply sane logging defaults (when using an Application).
  Defaults to logging to `stderr` so your application can write data to `stdout`
  for piping into other tools.


Extensions
==========

- SQLAlchemy - `pae.sqlalchemy <https://www.github.com/pyapp-org/pae.sqlalchemy>`_
- Redis - `pae.redis <https://www.github.com/pyapp-org/pae.redis>`_

Coming soon
-----------

Extensions for LDAP, Paramiko, SMTP, Boto.
