import pytest

from pathlib import Path

from pyapp.conf import settings

# Ensure settings are configured
settings.configure(["tests.settings"])


@pytest.fixture
def fixture_path() -> Path:
    return Path(__file__).parent / "fixtures"
