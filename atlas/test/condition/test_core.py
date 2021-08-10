from atlas.conditions import (
    true, false, ParamExists, IsParameter
)
from atlas.core.conditions import Statement, Comparable, Historical

import pytest

def test_true():
    assert bool(true)

def test_false():
    assert not bool(false)

def test_params(session):
    
    cond = ParamExists(mode="test", state="right")

    assert not bool(cond)
    session.parameters["mode"] = "test"
    
    assert not bool(cond)
    session.parameters["state"] = "wrong"

    assert not bool(cond)
    session.parameters["state"] = "right"

    assert bool(cond)

def test_is_parameter(session):
    cond = IsParameter(x="yes", y="yes")
    assert not bool(cond)

    session.parameters["x"] = "yes"
    assert not bool(cond)

    session.parameters["y"] = "yes"
    assert bool(cond)

    session.parameters["y"] = "no"
    assert not bool(cond)


# Test no unexpected errors in all
@pytest.mark.parametrize("cls", set(Statement.__subclasses__() + Comparable.__subclasses__() + Historical.__subclasses__()))
def test_magic_noerror(cls):
    if cls.__name__ in ('TaskSucceeded', 'DependFinish', 'TaskTerminated', 'TaskFinished', 'TaskFailed', 'DependFailure', 'TaskStarted', 'DependSuccess', 'TaskInacted', 'TaskRunning'):
        pytest.skip("Initing requires task as argument")
    str(cls())