###############
Getting Started
###############

In this section we will run through the processes of building an application with
``pyApp``.

App Layout
==========

We'll start with a simple application that accepts input from the command line
and combines it with a value from configuration.

The default ``pyApp`` configuration makes a number of assumptions as to how your
application is laid out, with each module within your application package
fulfilling a specific purpose. The easiest way to setup a basic app is to use
the ``pyApp`` Cookiecutter to generate an application.

Install cookie-cutter from pip and use the template to start your initial
project::

    pip install cookiecutter
    cookiecutter gh:pyapp-org/pyapp.cookiecutter


.. tip:: You can skip this step if you want to just get the info.


Project Structure
-----------------

The basic structure of a ``pyApp`` application package consists of the following::

    - myapp
      |- __init__.py          Standard Python package initialisation
      |- __main__.py          Standard Python main entry point
      |- cli.py               The CLI (referenced from __main__)
      |- default_settings.py  Definition of default runtime configuration
      |- checks.py            Application specific checks


``__init__.py``
---------------

The presence of an ``__init__.py`` file in a folder makes Python use the folder
as a package and contains initialisation code for the package. ``pyApp`` expects
this file to contain a number of special variables that provide information to
the framework on how to setup the application.

The special variables are as follows:

``__version__``
    The version number of the application, it is recommended that this be a
    semantic version. ``pyApp`` also provides tools for this to be fetched from
    the installed package list.

``__default_settings__``
    Either an absolute or relative reference (from the ``__init__`` file) to the
    applications default settings. This setting is optional and the default
    location is ``.default_settings``.

``__checks__``
    Either an absolute or relative reference (from the ``__init__`` file) to the
    applications checks file. This setting is optional and the default location
    is ``.checks``.

``__main__.py``
---------------

The main entry point for a Python application when referring to a package using
``python -m myapp``. The default cookiecutter application triggers the main
function in the *cli* module.

``cli``
-------

This is where the ``pyApp`` ``CliApplication`` instance is defined. The
``CliApplication`` class handles initialisation of application services before
handing over execution to the command handler of the command specified from the
CLI.

Adding CLI Commands
~~~~~~~~~~~~~~~~~~~

CLI commands are defined


``default_settings.py``
-----------------------

The default runtime settings for your application. These provide the defaults on
which environment/end user specific settings can be applied. This is a normal
Python module allowing for complex behaviours to be defined. Any variable that
consists of all upper-case characters (as well as `_`) is considered a setting
and is imported into the settings container.

Once an application has been initialised the final set of runtime settings is
available from the settings container ``pyapp.conf.settings``.

``checks.py``
-------------

The location for any application specific run time checks are defined and
registered. Checks allow your application to ensure configuration is correct or
to confirm aspects of the runtime environment are as they are expected to be.
This can included confirming access to a database or other services. These are
invaluable post deployment to confirm a successful deployment or to diagnose
problems.
