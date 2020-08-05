##########
Extensions
##########


Available Extensions
====================

pyApp Developed
---------------

Extensions available for use:

- `pyapp.aiobotocore <https://github.com/pyapp-org/pyapp.aiobotocore>`_ -
  Factory for `Async AWS client library <https://github.com/aio-libs/aiobotocore>`_
- `pyapp.aio_pika <https://github.com/pyapp-org/pyapp.aio_pika>`_ -
  Factory for `Async client for AMQP <https://github.com/mosquito/aio-pika/>`_
- `pyapp.redis <https://github.com/pyapp-org/pyapp.redis>`_ -
  Factory for `redis-py <https://github.com/andymccurdy/redis-py>`_
- `pyapp.sqlalchemy <https://github.com/pyapp-org/pyapp.sqlalchemy>`_ -
  Factory for `SQLALchemy <https://www.sqlalchemy.org>`_


Extensions in beta:

- `pyapp-messaging <https://github.com/pyapp-org/pyapp-messaging>`_ -
  Abstract messaging framework for interacting with Pub/Sub and Message Queues.

Extensions in development:

- `pyapp.boto3 <https://github.com/pyapp-org/pyapp.boto3>`_ -
  Factory for `AWS client library <https://boto3.amazonaws.com/v1/documentation/api/latest/index.html>`_
- `pyapp.smtp <https://github.com/pyapp-org/pyapp.SMTP>`_ -
  Interface to `smtplib <https://docs.python.org/3/library/smtplib.html>`_

.. note::
    The development status of these projects may have changed from when this
    documentation was generated, see the repository (or PyPi) of the extension
    package for up to date status.

Developing an Extension
=======================

An extension is a standard Python package that exports a known entry point that
pyApp uses to identify extensions.  This entry point will reference a class with
known attributes that pyApp recognises.

A Basic Project
---------------

An extensions consists of a standard Python project structure eg::

    ├┬ my_extension
    │└ __init__.py
    ├ README.rst
    ├ pyproject.toml
    ├ setup.cfg
    └ setup.py



The contents of which are:

``my_extension/__init__.py``
    The package init file, this file contains the extension entry point. While a
    package must container an Extension class every attribute on the class is optional.

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
    A gotcha when building extensions is attempting to access settings to early
    this is the reason for the ``ready`` event on the Extension class. Once ready
    has been called settings are setup and ready for use.

``README.rst``
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
