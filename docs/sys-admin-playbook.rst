System Admin Playbook
#####################

While pyApp offers a lot of features to help developers be more productive, it
also provides a suite of tools for Sysadmins to help identify application issues
and simplify operation of an application developed with pyApp.

.. tip::
  pyApp provides a CLI that provides a ``--help`` option at most locations, this
  is a great way to find out more about a command or what commands are available.

  All builtin commands include help using this method.


Deployment
==========

The recommended approach to deploy a pyApp application is using a virtual environment
(virtualenv or venv) or within a container (eg Docker). This keeps your application
self contained with only the expected dependencies installed.

pyApp uses automatic extension loading to get the default configuration loaded and
by using a container only the expected extensions will be available and loaded.


Output
------

By default pyApp configures logging to be directed to ``stderr`` and any report
output (of builtin tools) to be directed to ``stdout``, this allows for application
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
or to just change the behaviour of an application for testing. This can be done
via two methods:

1. Using the ``--settings`` command line argument eg::

    > my_application --settings production_settings

2. Using an Environment variable. The environment variable defaults to
   ``PYAPP_SETTINGS``, however, this can be changed by the development team to
   prevent naming clashes, the correct value is always reported when using the
   ``--help`` option.

Both of these options can be used at the same time, environment variables is
particularly useful in a Docker container.

Runtime settings can be defined in a number of ways:

- A python module

- A local JSON or YAML file

- A remote JSON or YAML file via HTTP(S)

See the `Conf.Loaders` section of the Reference guide for information on loading
different settings files.


Run-Time Checks
---------------

pyApp includes a checks framework designed for running environmental checks to
confirm that configuration is valid, services can be accessed (eg Databases,
External Hosts, SSH). This lets the application be verified quickly without
running any business processes.

To run the checks use::

  > my_application checks

  # With more detail

  > my_application checks --verbose


How do I
========

Common operations that need to performed by an operations team and how to do them.

How do I change the log level?
------------------------------

The log level can be changed by either:

1. Using the ``--log-level`` option on the command line

2. Setting the ``PYAPP_LOGLEVEL`` environment variable

.. note::
  The log-level environment variable can be renamed, use the ``--help`` option
  to get the current name.


What are the current settings?
------------------------------

What is the applications current configuration and what values are being used::

  > my_application settings

This command will list all of the current application settings, the log will
indicate what settings files are being loaded.


Where are the settings being loaded from?
-----------------------------------------

Using the settings command combined with DEBUG level logging reports not only
what settings file are being loaded, but each individual value from each file::

  > my_application --log-level DEBUG settings


What extensions are being loaded with the application?
------------------------------------------------------

All extensions that are available (without actually loading them) along with
their version can be obtained using the builtin ``extensions`` command::

  > my_application extensions


How do I perform a PIV (Post Implementation Verification) test?
---------------------------------------------------------------

The checks framework can provide the basis of a PIV test prior to running any
processes, this ensures the environment and any connectivity problems can be
identified before longer more complex processes are started.

How do I perform regular monitoring checks?
-------------------------------------------

The checks framework can be used to perform regular monitoring of the application
via a cron job. To simplify making use of this data the checks report has a tabular
output that can be processed as a Tab Separated output for easy parsing::

  > my_application checks --table

