#!/usr/bin/env python3
from pathlib import Path

from setuptools import setup

HERE = Path(__file__).parent

about = {}
exec((HERE / "pyapp" / "__version__.py").read_text(), about)


if __name__ == "__main__":
    setup(version=about["__version__"])
