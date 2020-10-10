Developers
==========

We welcome contributions to the pyApp project (and sub projects).

To get our PR accepted quickly please ensure the following requirements are
met:

- Install the `pre-commit <https://github.com/pre-commit/pre-commit>`_ hooks to
  ensure you code is formatted by `black <https://github.com/ambv/black>`_.

- Ensure your code has unit test coverage (using pyTest). Unittests should be
  designed to be as fast as possible.

- Ensure your code passes the pyLint checks (this is part of the automated build).

- Update the docs with the details if required.

- The API matters, ensure any features provide a nice API for end users.


The core pyApp package is intended to be light and mainly made up of plumbing
code. If you want to add support for a particular service or server an extension
is the way to do this.

See the *Developing an Extension* section of the extensions doc for guidance on
building your own extension.
