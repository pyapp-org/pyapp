Release 3.4
===========

Features
--------

- Backported Injection from 4.x (although simplified to work without type annotations)

Bugfixes
--------

- Switch exit to sys.exit (exit is not a builtin but a implimentation detail, this causes issues when using freezing tools)

