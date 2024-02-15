from unittest.mock import Mock, patch

import pyapp.conf
import pytest
from pyapp import multiprocessing


def test_roundtrip_settings(monkeypatch):
    source_settings = pyapp.conf.Settings()
    source_settings.__dict__["FOO"] = "foo"
    source_settings.__dict__["BAR"] = "bar"
    source_settings.SETTINGS_SOURCES.append("self")
    with patch("pyapp.conf.settings", source_settings):
        pickled_settings = multiprocessing.prepare_settings()

    target_settings = pyapp.conf.Settings()
    with patch("pyapp.conf.settings", target_settings):
        multiprocessing.pyapp_initializer(pickled_settings, None, ())

        assert target_settings.FOO == source_settings.FOO
        assert target_settings.BAR == source_settings.BAR
        assert target_settings.SETTINGS_SOURCES == source_settings.SETTINGS_SOURCES


def test_roundtrip_settings__with_initializer(monkeypatch):
    mock_initializer = Mock()

    source_settings = pyapp.conf.Settings()
    source_settings.__dict__["FOO"] = "foo"
    source_settings.SETTINGS_SOURCES.append("self")
    with patch("pyapp.conf.settings", source_settings):
        pickled_settings = multiprocessing.prepare_settings()

    target_settings = pyapp.conf.Settings()
    with patch("pyapp.conf.settings", target_settings):
        multiprocessing.pyapp_initializer(pickled_settings, mock_initializer, (1, 2))

        assert target_settings.FOO == source_settings.FOO
        assert target_settings.SETTINGS_SOURCES == source_settings.SETTINGS_SOURCES

    mock_initializer.assert_called_with(1, 2)


class TestPool:
    def test_call_pool_and_with_invalid_initializer(self):
        with pytest.raises(TypeError):
            pyapp.multiprocessing.Pool(
                processes=2, initializer=123, initargs=("a", "b")
            )
