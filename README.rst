######################################
pyApp - A python application framework
######################################

*Let us handle the boring stuff!*

.. image:: https://readthedocs.org/projects/pyapp/badge/?version=latest
   :target: https://docs.pyapp.info/
   :alt: ReadTheDocs

.. image:: https://img.shields.io/travis/pyapp-org/pyapp.svg?style=flat
   :target: https://travis-ci.org/pyapp-org/pyapp
   :alt: Travis CI Status

.. image:: https://img.shields.io/pypi/wheel/pyapp.svg
   :target: https://pypi.io/pypi/pyapp/

.. image:: https://api.codeclimate.com/v1/badges/58f9ffacb711c992610d/test_coverage
   :target: https://codeclimate.com/github/pyapp-org/pyapp/test_coverage
   :alt: Test Coverage

.. image:: https://api.codeclimate.com/v1/badges/58f9ffacb711c992610d/maintainability
   :target: https://codeclimate.com/github/pyapp-org/pyapp/maintainability
   :alt: Maintainability

.. image:: https://img.shields.io/pypi/v/pyapp.svg
   :target: https://pypi.io/pypi/pyapp/
   :alt: Latest Version

.. image:: https://img.shields.io/pypi/pyversions/pyapp.svg
   :target: https://pypi.io/pypi/pyapp/

.. image:: https://img.shields.io/pypi/l/pyapp.svg
   :target: https://pypi.io/pypi/pyapp/

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/ambv/black
   :alt: Once you go Black...


Many features inspired by Django, but modified to be more general for use
outside of web applications.

With pyApp 4.0, versions of Python < 3.6 are no longer supported.


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
  deterministic startup, addition of commands to the CLI and the ability to
  register checks and default settings.
- Application - Provides a extensible and simple CLI interface for starting
  running commands, comes with built-in commands to support Checks, report
  settings/extensions.
- Logging - Initialise and apply sane logging defaults (when using an Application).
  Defaults to logging to `stderr` so your application can write data to `stdout`
  for piping into other tools.


Extensions
==========

- SQLAlchemy - `pyapp.sqlalchemy <https://www.github.com/pyapp-org/pyapp.sqlalchemy>`_
- Redis - `pyapp.redis <https://www.github.com/pyapp-org/pyapp.redis>`_
- AIOBotocore - `pyapp.aiobotocore <https://www.github.com/pyapp-org/pyapp.aiobotocore>`_

In development
--------------

- SMTP - `pyapp.SMTP <https://www.github.com/pyapp-org/pyapp.SMTP>`_
- Boto3 - `pyapp.boto3 <https://www.github.com/pyapp-org/pyapp.boto3>`_

Coming soon
-----------

Extensions for LDAP, Paramiko.


Contributions
=============

Contributions are most welcome, be it in the form of a extension and factories
for your favourite service client of bug reports, feature enhancements.

The core of pyApp is intended to remain simple and only provide required features
with extensions providing optional more specific functionality.

