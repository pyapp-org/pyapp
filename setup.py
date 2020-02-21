import os
from setuptools import setup

here = os.path.dirname(__file__)

about = {}
exec(open(os.path.join(here, "pyapp/__version__.py")).read(), about)

setup(version=about["__version__"])

