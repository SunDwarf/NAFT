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


@with_engine
def some_other_func(a, b):
    return some_func(a), b


def test_python_is_sane():
    assert True, "what"


def test_function_is_wrapped():
    assert isinstance(some_func, NFunction), "some_func should be wrapped in an NFunction instance"


def test_function_returns_nrunnable():
    assert isinstance(some_func(), _NRunnableObject)
    assert some_func(1).run_natively() == 1


def test_simple_run():
    engine = NAFTEngine()
    assert engine.run_function(some_func(2)) == 2


def test_chained_function_calls():
    engine = NAFTEngine()
    assert engine.run_function(some_other_func(1, 2)) == (1, 2)


@pytest.mark.xfail(reason="Passed no arguments", strict=True)
def test_too_many_args():
    # Create the engine to be used.
    engine = NAFTEngine()
    assert not engine.run_function(some_func())
