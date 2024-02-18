import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent.absolute()
SRC_PATH = HERE.parent.parent / "src"

sys.path.insert(0, SRC_PATH.as_posix())

# Ensure settings are configured
from pyapp.conf import settings  # noqa: E402

settings.configure(["tests.settings"])

# Enable the pytester plugin
pytest_plugins = "pytester"


@pytest.fixture
def fixture_path() -> Path:
    return Path(__file__).parent / "fixtures"
