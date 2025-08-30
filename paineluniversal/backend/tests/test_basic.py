import pytest

def test_basic():
    assert 1 + 1 == 2

def test_api_import():
    from app import main_simple
    assert hasattr(main_simple, 'app')

