from pathlib import Path
from setuptools import setup

here = Path(__file__).parent

about = {}
with (here / "pyapp/__version__.py").open() as f:
    exec(f.read(), about)

setup(version=about["__version__"])
