########
Settings
########

Settings are a key part of the pyApp framework and are utilised to control many
aspects of the framework. This section goes into how settings are compiled and
some of the ways to use them to created more configurable applications that can
more easily adapt to change.


What are settings?
==================

Default Settings
----------------

Both an application and each extension that is loaded provide a set of default settings.
Default settings can be thought of as both the definition of available settings and
the source of the initial settings value.

Runtime Settings
----------------

These are the settings supplied to the application when it is started. These can be
specified as either a command line flag or via and environment variable. Typically
runtime settings are environment specific eg settings for development, staging or
production environments.

.. tip:: The default CLI includes the ``--settings`` option that is used to
          specify runtime settings at startup.

How Settings are Compiled?
==========================

Settings are collected for a number of sources when an application starts up.
These settings are then combined into the settings collection to produce the final
complete set of settings.

Settings are applied in the following order:

- Default settings for each extension (that supplies settings)

- Default settings for the application

- Runtime settings


Changing Settings at Runtime
============================


Common Pattens
==============
