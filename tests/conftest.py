import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent.absolute()
SRC_PATH = HERE.parent.parent / "src"

sys.path.insert(0, SRC_PATH.as_posix())

# Enable the pytester plugin
pytest_plugins = "pytester"


@pytest.fixture(scope="session", autouse=True)
def configure_settings():
    # Ensure settings are configured
    from pyapp.conf import settings  # noqa: PLC0415

    settings.configure(["tests.settings"])


@pytest.fixture
def fixture_path() -> Path:
    return Path(__file__).parent / "fixtures"
