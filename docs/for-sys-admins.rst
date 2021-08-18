For System Admins
#################

While pyApp offers a lot of features to help developers be more productive, it
also provides a suite of tools for Sysadmins to simplify the operation and management
of an application developed with pyApp and to help identify application issues.

.. tip::
  The pyApp CLI provides a ``--help`` option, this is a great way to find out more
  about a command or what options are available.

  All builtin commands include help using this method.


Deployment
==========

The recommended approach for deploying a pyApp application is in a Python virtual
environment (virtualenv or venv) or within a container (eg Docker). This keeps the
application self contained with only the expected dependencies installed.

pyApp uses automatic extension loading to get the default configuration loaded using
an isolated virtual environment or container ensures that only the expected
extensions will be available and loaded.


Output
------

By default pyApp configures logging to be directed to ``stderr`` and any report
output (of builtin tools) to be directed to ``stdout``, allowing application
output to be piped to other tools or files.


Exit Codes
----------

pyApp has a top level exception handler that will put a stacktrace of any unhandled
exceptions into the log before passing the exception onto Pythons standard mechanisms.

Keyboard Interruptions (Ctrl+C) are caught and will return -2.

A normal exit will generate the standard 0 exit code.


Run-time Settings
-----------------

Settings can be supplied at run time to provide environmental specific configuration
or to just change the behaviour of an application for testing. This is achieved using
one of two methods:

1. Using the ``--settings`` command line argument eg::

    > my_application --settings production_settings

2. Using an Environment variable. The environment variable defaults to
   ``PYAPP_SETTINGS``, however, this can be changed by the development team to
   prevent naming clashes, the correct value is always reported from the
   ``--help`` option.

Both of these options can be used at the same time.

Runtime settings can be defined in a number of ways:

- A python module
- A local text file in a supported format
- A remote file via HTTP(S) in a supported format

Supported formats include JSON, `YAML <https://yaml.org/>`_, `TOML <https://toml.io/>`_.

See the `Conf.Loaders` section of the Reference guide for information on loading
different settings files.


Run-Time Checks
---------------

The checks framework is designed for running application checks to confirm that
configuration is valid, services can be accessed (eg Databases, External Hosts,
SSH) or any other check that can be used to determine the current execution environment
is operating correctly. This lets the application be verified quickly without
running any business processes.

To run the checks use::

  > my_application checks

  # With more detail

  > my_application checks --verbose


How do I
========

This sections covers common operations that are performed by a administrative team
during BAU (Business As Usual) operation.

How do I change the log level?
------------------------------

The log level can be changed by either:

1. Using the ``--log-level`` option on the command line

2. Setting the ``PYAPP_LOGLEVEL`` environment variable

.. note::
  The log-level environment variable can be renamed, use the ``--help`` option
  to get the current variable name.


What are the current settings?
------------------------------

To view a report of all current configuration values use::

  > my_application settings

To determine what files are being loaded to generate these settings see the log
output.


Where are the settings being loaded from?
-----------------------------------------

Using the settings command combined with DEBUG level logging reports not only
what settings file are being loaded, but each individual value being merged into
from each file::

  > my_application --log-level DEBUG settings


What extensions are being loaded with the application?
------------------------------------------------------

All extensions that are available (without actually loading them) along with
their version can be obtained using the builtin ``extensions`` command::

  > my_application extensions


How do I perform a PIV (Post Implementation Verification) test?
---------------------------------------------------------------

The checks framework can provide the basis of a PIV test.


How do I perform regular monitoring checks?
-------------------------------------------

The checks framework can be used to perform regular monitoring of the application
via a cron job. To simplify making use of this data the checks report has a tabular
output that can be processed as a Tab Separated output for easy parsing::

  > my_application checks --table

Any failures will also result in a non-zero status code.
