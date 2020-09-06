.. PyApp documentation master file, created by
   sphinx-quickstart on Thu Jan 12 12:26:34 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.



Welcome to PyApp's documentation!
=================================

*Let us handle the boring stuff!*

As of pyApp 4.0, Python < 3.6 is no longer supported.

+---------+---------------------------------------------------------------------------------------+
| Docs    | .. image:: https://readthedocs.org/projects/pyapp/badge/?version=latest               |
|         |    :target: https://docs.pyapp.info/                                                  |
|         |    :alt: ReadTheDocs                                                                  |
+---------+---------------------------------------------------------------------------------------+
| Build   | .. image:: https://img.shields.io/travis/pyapp-org/pyapp.svg?style=flat               |
|         |    :target: https://travis-ci.org/pyapp-org/pyapp                                     |
|         |    :alt: Travis CI Status                                                             |
|         | .. image:: https://api.dependabot.com/badges/status?host=github&repo=pyapp-org/pyapp  |
|         |    :target: https://dependabot.com                                                    |
|         |    :alt: Dependabot Status                                                            |
+---------+---------------------------------------------------------------------------------------+
| Quality | .. image:: https://api.codeclimate.com/v1/badges/58f9ffacb711c992610d/maintainability |
|         |    :target: https://codeclimate.com/github/pyapp-org/pyapp/maintainability            |
|         |    :alt: Maintainability                                                              |
|         | .. image:: https://api.codeclimate.com/v1/badges/58f9ffacb711c992610d/test_coverage   |
|         |    :target: https://codeclimate.com/github/pyapp-org/pyapp/test_coverage              |
|         |    :alt: Test Coverage                                                                |
|         | .. image:: https://img.shields.io/badge/code%20style-black-000000.svg                 |
|         |    :target: https://github.com/ambv/black                                             |
|         |    :alt: Once you go Black...                                                         |
+---------+---------------------------------------------------------------------------------------+
| Package | .. image:: https://img.shields.io/pypi/v/pyapp                                        |
|         |    :target: https://pypi.io/pypi/pyapp/                                               |
|         |    :alt: Latest Version                                                               |
|         | .. image:: https://img.shields.io/pypi/pyversions/pyapp                               |
|         |    :target: https://pypi.io/pypi/pyapp/                                               |
|         | .. image:: https://img.shields.io/pypi/l/pyapp                                        |
|         |    :target: https://pypi.io/pypi/pyapp/                                               |
|         | .. image:: https://img.shields.io/pypi/wheel/pyapp                                    |
|         |    :alt: PyPI - Wheel                                                                 |
|         |    :target: https://pypi.io/pypi/pyapp/                                               |
+---------+---------------------------------------------------------------------------------------+

pyApp takes care of the boring boilerplate code for building a CLI, managing
settings and much more so you can focus on your business logic.


So what do we handle?
=====================

- Configuration - Loading, merging your settings from different sources

  + Python modules
  + File and HTTP(S) endpoints for JSON and YAML files.

- Instance Factories - Configuration of plugins, database connections, or just
  implementations of an ``ABC``.
  Leveraging settings to make setup of your application easy and reduce coupling.

- Dependency Injection - Easy to use dependency injection without complicated setup.

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
