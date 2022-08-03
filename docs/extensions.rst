##########
Extensions
##########

Developing an Extension
=======================

A pyApp extension is a standard Python package that exports an entry point that
pyApp utilises to load/activate the code.  The entry point will reference a class
with attributes that pyApp recognises.

A Basic Project
---------------

The structure of an extension is similar to any other Python package.

With Setuptools::

    ├┬ my_extension
    │└ __init__.py
    ├ README.rst
    ├ setup.cfg
    └ setup.py


With Poetry::

    ├┬ my_extension
    │└ __init__.py
    ├ README.rst
    ├ pyproject.toml
    ├ poetry.lock


The contents of each file:

``my_extension/__init__.py``
    The package init file, this file contains the extension entry point. While a
    package must contain an Extension class every attribute on the class is optional.

    .. code-block:: python

        class Extension:
            """
            My pyApp Extension
            """

            default_settings = ".default_settings"
            checks = ".checks"

            @staticmethod
            def register_commands(root):
                """
                Register custom commands with pyApp.
                """

            @staticmethod
            def ready():
                """
                Method called once pyApp has configured environment
                """


.. tip::
    One gotcha when building extensions is attempting to access settings too early
    before they have been loaded by pyApp, this is the use of the ``ready`` event
    on the Extension class. The ``ready`` method will be called once all initialisation
    activities have been completed and settings etc are ready for use.


``README.rst`` or ``README.md``
    While not strictly necessary a README document is *highly recommended* and is
    included in the package as the long description.

    .. code-block:: rst

        ##################
        My pyApp Extension
        ##################

        Information about my extension


Using Setuptools
~~~~~~~~~~~~~~~~

``setup.cfg``
    Defines the metadata and configuration used to build a package, this is also
    where the entry point used identify you extension is defined.

    .. code-block:: ini

        [metadata]
        name = my-extension
        version = "0.1"
        author = Author
        author-email = author@example.com
        description = Blurb about my extension
        long-description = file: README.rst
        url = https://github.com/author/my-extension
        platforms = any
        license = BSD-3-Clause

        [options]
        python_requires = >=3.6
        packages = find:
        setup_requires =
            setuptools >=38.3
        install_requires =
            pyapp >=4.3.0

        [options.entry_points]
        # Used by pyApp to recognise my_extension
        pyapp.extensions =
            my-extension = my_extension:Extension


``setup.py``
    Script that trigger ``setuptools`` to build a package.

    .. code-block:: python

        import setuptools

        setuptools.setup()


Using poetry
~~~~~~~~~~~~

``pyproject.toml``

    Defines the metadata and configuration used to build a package, this is also
    where the entry point used identify you extension is defined.

    .. code-block:: toml

        [build-system]
        requires = ["poetry>=0.12"]
        build-backend = "poetry.masonry.api"

        [tool.poetry]
        name = "my-extension"
        version = "0.1"
        description = "Blurb about my extension"
        authors = ["Author <author@example.com>"]
        license = "BSD-3-Clause"
        packages = [
            { include = "my_extension" },
        ]
        readme = "README.rst"
        repository = "https://github.com/author/my-extension"

        [tool.poetry.dependencies]
        python = "^3.6"
        pyapp = "^4.3.0"

        [tool.poetry.dev-dependencies]
        pytest = "^5.4.3"
        pytest-cov = "^2.10.0"

        [tool.poetry.plugins."pyapp.extensions"]
        "my-extension" = "my_extension:Extension"


Available Extensions
====================

pyApp Developed
---------------

🔌 SQLAlchemy - `pyapp.sqlalchemy`_

🔌 Redis - `pyapp.redis`_

In Beta
~~~~~~~

🐛 Rollbar - `pyapp.rollbar`_

📧 AIO SMTPlib - `pyapp.aiosmtplib`_ Extension for aiosmtplib

☁ Boto3 - `pyapp.boto3`_

☁ AIOBotocore - `pyapp.aiobotocore`_

📨 Messaging - `pyapp.messaging`_ - Extension to provide abstract interfaces for Message Queues.

- 📨 AWS Messaging - `pyapp.messaging-aws`_ - Messaging extension for AWS (SQS/SNS)

In development
~~~~~~~~~~~~~~

📧 SMTP - `pyapp.SMTP`_

📨 Aio-Pika - `pyapp.aiopika`_ - Messaging extension for pika (RabbitMQ/AMQP)

🔌 PySpark - `pyapp.pyspark`_ - Extension for PySpark

🔎 Elastic Search - `pyapp.elasticsearch`_ - Extension for Elasticsearch

Coming soon
-----------

📨 AMQP Messaging - Messaging extension for AMQP (RabbitMQ)

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

.. note::
    The development status of these projects may have changed from when this
    documentation was generated, see the repository (or PyPi) of the extension
    package for up to date status.
