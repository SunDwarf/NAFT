"""
Engine tests.

Used to test the core of the engine, without any specific in-depth tests.
"""
import pytest

from naft.engine import NAFTEngine
from naft.wrapper import with_engine, NFunction, _NRunnableObject


@with_engine
def some_func(a):
    return a


def test_python_is_sane():
    assert True


def test_function_is_wrapped():
    assert isinstance(some_func, NFunction), "some_func should be wrapped in an NFunction instance"


def test_function_returns_nrunnable():
    assert isinstance(some_func(), _NRunnableObject)
    assert some_func(1).run_natively() == 1


@pytest.mark.xfail
def test_too_many_args():
    # Create the engine to be used.
    engine = NAFTEngine()
    assert not some_func()
