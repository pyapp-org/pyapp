"""Compatibility between Python Releases and Operating Systems."""

__all__ = ("async_run", "ROOT_NAME", "is_root_user")

import os
import sys
from asyncio import run as async_run

if sys.platform.startswith("win"):
    from ctypes import windll

    ROOT_NAME = "Administrator"

    def is_root_user() -> bool:
        """This is a root user."""
        return bool(windll.shell32.IsUserAnAdmin())

else:
    ROOT_NAME = "root"

    def is_root_user() -> bool:
        """This is a root user."""
        return bool(os.getuid() == 0)
