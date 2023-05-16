Welcome to PyApp's documentation!
=================================

A simple python application framework *let pyApp handle the boring stuff!*

As of pyApp 4.3, Python < 3.8 is no longer supported.

+---------+------------------------------------------------------------------------------------------------------------+
| Docs    | .. image:: https://readthedocs.org/projects/pyapp/badge/?version=latest                                    |
|         |    :target: https://docs.pyapp.info/                                                                       |
|         |    :alt: ReadTheDocs                                                                                       |
+---------+------------------------------------------------------------------------------------------------------------+
| Build   | .. image:: https://api.dependabot.com/badges/status?host=github&repo=pyapp-org/pyapp                       |
|         |    :target: https://dependabot.com                                                                         |
|         |    :alt: Dependabot Status                                                                                 |
+---------+------------------------------------------------------------------------------------------------------------+
| Quality | .. image:: https://sonarcloud.io/api/project_badges/measure?project=pyapp-org_pyapp&metric=sqale_rating    |
|         |    :target: https://sonarcloud.io/dashboard?id=pyapp-org_pyapp                                             |
|         |    :alt: Maintainability                                                                                   |
|         | .. image:: https://sonarcloud.io/api/project_badges/measure?project=pyapp-org_pyapp&metric=security_rating |
|         |    :target: https://sonarcloud.io/project/security_hotspots                                                |
|         |    :alt: Security                                                                                          |
|         | .. image:: https://sonarcloud.io/api/project_badges/measure?project=pyapp-org_pyapp&metric=coverage        |
|         |    :target: https://sonarcloud.io/code?id=pyapp-org_pyapp                                                  |
|         |    :alt: Test Coverage                                                                                     |
|         | .. image:: https://img.shields.io/badge/code%20style-black-000000.svg                                      |
|         |    :target: https://github.com/ambv/black                                                                  |
|         |    :alt: Once you go Black...                                                                              |
+---------+------------------------------------------------------------------------------------------------------------+
| Package | .. image:: https://img.shields.io/pypi/v/pyapp                                                             |
|         |    :target: https://pypi.io/pypi/pyapp/                                                                    |
|         |    :alt: Latest Version                                                                                    |
|         | .. image:: https://img.shields.io/pypi/pyversions/pyapp                                                    |
|         |    :target: https://pypi.io/pypi/pyapp/                                                                    |
|         | .. image:: https://img.shields.io/pypi/l/pyapp                                                             |
|         |    :target: https://pypi.io/pypi/pyapp/                                                                    |
|         | .. image:: https://img.shields.io/pypi/wheel/pyapp                                                         |
|         |    :alt: PyPI - Wheel                                                                                      |
|         |    :target: https://pypi.io/pypi/pyapp/                                                                    |
+---------+------------------------------------------------------------------------------------------------------------+

pyApp takes care of the application framework code, managing settings and much
more so you can focus on your business logic.


So what does pyApp handle?
==========================

- Configuration - Loading, merging your settings from different sources

  + Python modules
  + File and HTTP(S) endpoints for JSON and YAML files.

- Instance Factories - Configuration of plugins, database connections, or just
  implementations of an ``ABC``.
  Leveraging settings to make setup of your application easy and reduce coupling.

- Dependency Injection - Easy to use dependency injection without complicated setup.

- Feature Flags - Simple methods to enable and disable features in your application
  at runtime.

- Checks - A framework for checking settings are correct and environment is
  operating correctly (your ops team will love you)?

- Extensions - Extend the basic framework with extensions. Provides deterministic
  startup, extension of the CLI and the ability to register checks and extension
  specific default settings.

- Application - Provides a extensible and simple CLI interface for running
  commands (including async), comes with built-in commands to execute check, setting
  and extension reports.

- Logging - Initialise and apply sane logging defaults.

- Highly tested and ready for production use.


Installation
============

Installation with pip::

   pip install pyapp


Table of Contents
=================

.. toctree::
   :maxdepth: 2

   getting-started
   sys-admin-playbook
   recipes/index
   reference/index
   extensions
   developers
   change-history

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
