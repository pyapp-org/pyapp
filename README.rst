######################################
pyApp - A python application framework
######################################

*Let us handle the boring stuff!*

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

pyApp takes care of the boring boilerplate code for building a CLI, managing
settings and much more so you can focus on your application logic.

So what does pyApp handle?
==========================

- **Configuration** - Loading, merging your settings from different sources

  + Python modules
  + File and HTTP(S) endpoints for JSON and YAML files.

- **Instance Factories** - Configuration of plugins, database connections, or just
  implementations of an ``ABC``.
  Leveraging settings to make setup of your application easy and reduce coupling.

- **Dependency Injection** - Easy to use dependency injection without complicated setup.

- **Checks** - A framework for checking settings are correct and environment is
  operating correctly (your ops team will love you)?

- **Extensions** - Extend the basic framework with extensions. Provides deterministic
  startup, extension of the CLI and the ability to register checks and extension
  specific default settings.

- **Application** - Provides a extensible and simple CLI interface for running
  commands (including async), comes with built-in commands to execute check, setting
  and extension reports.

- **Logging** - Initialise and apply sane logging defaults.

- Highly tested and ready for production use.


Extensions
==========

- 🔌 SQLAlchemy - `pyapp.sqlalchemy`_
- 🔌 Redis - `pyapp.redis`_

In Beta
-------

- 🐛 Rollbar - `pyapp.rollbar`_

- 📧 AIO SMTPlib - `pyapp.aiosmtplib`_ Extension for aiosmtplib

- ☁ Boto3 - `pyapp.boto3`_

- ☁ AIOBotocore - `pyapp.aiobotocore`_

- 📨 Messaging - `pyapp.messaging`_ - Extension to provide abstract interfaces for Message Queues.

  - 📨 AWS Messaging - `pyapp.messaging-aws`_ - Messaging extension for AWS (SQS/SNS)

In development
--------------

- 📧 SMTP - `pyapp.SMTP`_

- 📨 Aio-Pika - `pyapp.aiopika`_ - Messaging extension for pika (RabbitMQ/AMQP)

- 🔌 PySpark - `pyapp.pyspark`_ - Extension for PySpark

- 🔎 Elastic Search - `pyapp.elasticsearch`_ - Extension for Elasticsearch

Coming soon
-----------

- 📨 AMQP Messaging - Messaging extension for AMQP (RabbitMQ)


.. _pyapp.sqlalchemy: https://www.github.com/pyapp-org/pyapp.sqlalchemy
.. _pyapp.redis: https://www.github.com/pyapp-org/pyapp.redis
.. _pyapp.aiobotocore: https://www.github.com/pyapp-org/pyapp.aiobotocore
.. _pyapp.SMTP: https://www.github.com/pyapp-org/pyapp.SMTP
.. _pyapp.boto3: https://www.github.com/pyapp-org/pyapp.boto3
.. _pyapp.rollbar: https://www.github.com/pyapp-org/pyapp.rollbar
.. _pyapp.aiosmtplib: https://www.github.com/pyapp-org/pyapp.aiosmtplib
.. _pyapp.messaging: https://www.github.com/pyapp-org/pyapp-messaging
.. _pyapp.messaging-aws: https://www.github.com/pyapp-org/pyapp-messaging-aws
.. _pyapp.aiopika: https://www.github.com/pyapp-org/pyapp.aiopika
.. _pyapp.pyspark: https://www.github.com/pyapp-org/pyapp.pyspark
.. _pyapp.elasticsearch: https://www.github.com/pyapp-org/pyapp.elasticsearch


Contributions
=============

Contributions are most welcome, be it in the form of a extension and factories
for your favourite service client of bug reports, feature enhancements.

The core of pyApp is intended to remain simple and only provide required features
with extensions providing optional more specific functionality.

