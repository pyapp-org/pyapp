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

    > pip install cookiecutter
    > cookiecutter gh:pyapp-org/pyapp.cookiecutter


Project Structure
-----------------

The basic structure of a ``pyApp`` application package consists of the following::

    - myapp
      |- __init__.py          Python package initialisation
      |- __main__.py          Python main entry point
      |- cli.py               The CLI (referenced from __main__)
      |- default_settings.py  Definition of default runtime configuration
      |- checks.py            Application specific checks


``__init__.py``
---------------

The presence of an ``__init__.py`` file in a folder makes Python use the folder
as a package and contains initialisation code for the package. ``pyApp`` also
uses this file to find information for the application.

``__version__``
    The version number of the application, it is recommended that this be a
    semantic version. ``pyApp`` also provides tools for this to be fetched from
    the installed package list.


``__main__.py``
---------------

The main entry point for a Python application when referring to a package using
``python -m myapp``. The default cookiecutter application triggers the main
function in the *cli* module.

``cli``
-------

This is where the ``pyApp`` ``CliApplication`` instance is defined. The
``CliApplication`` class handles initialisation of application services before
handing over execution to the command handler of the command requested by the
CLI.


Setting up the CLI
~~~~~~~~~~~~~~~~~~

Adding a CLI consists of two steps, defining a ``CliApplication`` instance and
using the ``CliApplication.command`` decorator to functions to add commands to
your application.

First create a ``CliApplication`` instance:

.. code-block:: python

    from pyapp.app import CliApplication

    # Define our application instance
    app = CliApplication(
        description="My Application"
    )

    # Define our main entry point
    main = app.dispatch

``CliApplication`` has many options to customise how it works, these are all
provided with defaults but can be customised to change the behaviour, see the
API documentation for more information on other options.

Next CLI commands are created by applying the ``CliApplication.command`` argument
to a python function.

.. code-block:: python

  @app.command
  def greeting(name: str, *, greeting: str = "Hello"):
      """
      Provide a greeting
      """
      print(f"{greeting} {name}")

This example adds the `greeting` command to the CLI that requires a name and
allows for an optional greeting to be provided. It can be called using::

  > my_app greeting Guido --greeting Hallo
  Hallo Guido


Application Settings
~~~~~~~~~~~~~~~~~~~~

All of your applications settings are defined in the ``default_settings.py``
file that is located in your applications main package. These settings are
loaded by the CliApplication on startup and combine with settings from pyApp
extensions as well as runtime settings.

The default settings file is a normal python module allows for complex
behaviours to be defined. Any variable that consists of all upper-case
characters (including `_`) is considered a setting and is imported into the
settings container.

Once an application has been initialised the final set of runtime settings is
available from the settings container ``pyapp.conf.settings``:

.. code-block:: python

    from pyapp.conf import settings

    print(settings.MY_SETTING)


Runtime Checks
~~~~~~~~~~~~~~

These are functions that are called by the checks report to perform a check
against the current settings to assert that the current runtime environment is
correct. This can include:

- Checking settings are valid
- Confirming connectivity/access to a database
- Checking free space on the filesystem

These checks can help to diagnose issues, perform basic validation of the
runtime environment and provide application monitoring.

A check is defined by:

.. code-block:: python

    from pyapp import checks

    @checks.register
    def debug_is_enabled(settings, **_):
        if settings.DEBUG:
            return checks.Warning("Debug mode is enabled")

In this example a check returns a warning if DEBUG is ``True`` in settings.
