####################
Sphinx Documentation
####################

Integration with `Sphinx`_ to enable automatic generation of documentation from
your application.

Built on top of the `sphinx.ext.autodoc` extension.

This extension is used to generate the `base-settings <../conf/base-settings.html>`_ documentation for pyApp.

.. _Sphinx: http://sphinx-doc.org/

Installation
============

To install the Sphinx extension, add:

Add ``sphinx.ext.autodoc`` and ``pyapp.documentation.sphinx`` to the ``extensions``
list in your Sphinx `conf.py` file.

.. code-block:: python

  # Add any Sphinx extension module names here, as strings. They can be
  # extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
  # ones.
  extensions = [
      "sphinx.ext.autodoc",
      "pyapp.documentation.sphinx",
  ]


Documenting Settings
====================

**\.. autopyapp-settings:: name**

  This directive will generate documentation of the settings defined in the specified module.

  **options**

  \:noindex:
    If specified, the settings will not be indexed in the table of contents.

  \:grouped:
    If specified, the settings keys will be grouped by :py:class:`pyapp.typed_settings.SettingsDef`.

  \:sorted:
    If specified, the settings keys will be sorted.

Example:

.. code-block::

    .. autopyapp-settings:: myapp.default_settings

