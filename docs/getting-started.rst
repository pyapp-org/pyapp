###############
Getting Started
###############

In this tutorial we will run through the basics of an application that uses
`pyApp` and how to get yourself up and running.


Installation
============

`pyApp` is available on PyPI to install using your favourite package management
tool eg::

    pip install pyapp


Initial app
===========

There are a few requirements that come with a basic app. The easiest way to
setup a basic app is to use the `pyApp` Cookiecutter and to generate a basic
project.

Install cookie-cutter from pip and use the template to start your initial
project::

    pip install cookiecutter
    cookiecutter gh:pyapp-org/pyapp.cookiecutter


.. info:: You can skip this step if you want to just get the info.


Project Structure
-----------------

The basic structure of a pyApp project consists of the following files::

    - myapp
      |- __init__.py          Standard Python package initialisation
      |- __main__.py          Standard Python main entry point
      |- default_settings.py  Main settings definition for app
      |- checks.py            Application specific checks


__init__.py
-----------

This is a standard Python file used to define a folder as a Python package as
well as provide a location for initialisation code. In `pyApp` the root file
also contains a number of special variables that provide information to the
framework on how to setup the application.

The special variables are as follows:

`__version__`
    The version number of the application, it is recommended that this be a
    semantic version. `pyApp` also provides tools for this to be fetched from
    the installed package list.

`__default_settings__`
    Either an absolute or relative reference (from the `__init__` file) to your
    applications default settings. This setting is optional and the default
    location is `.default_settings`.

`__checks__`
    Either an absolute or relative reference (from the `__init__` file) to your
    applications checks file. This setting is optional and the default location
    is `.checks`.

__main__.py
-----------

The main entry point for a Python application when referring to a package using
`python -m myapp`. This is where the `pyApp` `CliApplication` instance is
defined. The `CliApplication` class handles initialisation of application
services before handling dispatch to a command handler of the command provided
from the CLI.

default_settings.py
-------------------

The default settings for your application. These provide the base on top of
which end user specific settings can be applied. This is just a Python file to
allow for complex behaviours to be defined. Any variable that consists of all
upper-case characters (as well as `_`) is considered a setting and is imported
into the settings container.

Once an application has been initialised your settings are available from the
settings container `pyapp.conf.settings`.

checks.py
---------


