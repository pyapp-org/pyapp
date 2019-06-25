import pyapp


def test_metadata():
    assert pyapp.__author__.startswith("Tim")
    assert pyapp.__version__ is not None
