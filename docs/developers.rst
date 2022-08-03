Developers
==========

Contributions to the pyApp project (and sub projects) are welcome.

To get a PR accepted quickly please ensure the following requirements are
met:

- Install the `pre-commit <https://github.com/pre-commit/pre-commit>`_ hooks to
  ensure:

  - All code is formatted by `black <https://github.com/ambv/black>`_
  - Code passes PyLint checks (this is part of the automated build)

- Ensure code has unit test coverage (using pyTest). Unittests should be
  designed to be as fast as possible.

- Documentation has been updated to reflect the change

- The API matters, ensure any features provide a nice API for end users.

The core pyApp package is intended to be light and primarily made up of plumbing
code. To add support for a particular service or server a new pyApp extension is
the way to achieve this.

See the `Developing an Extension`_ section of the extensions doc for guidance on
building a new extension.

.. _Developing an Extension:
