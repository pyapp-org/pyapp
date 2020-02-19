#!/usr/bin/env python3
from pathlib import Path

from setuptools import setup

here = Path(__file__).parent

about = {}
exec((here / "pyapp" / "__version__.py").read_text(), about)


if __name__ == "__main__":
    setup(version=about["__version__"])
