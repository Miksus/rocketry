
import re

import pytest

from rocketry.core import BaseCondition
from rocketry.conditions import FuncCond
from rocketry.parse.condition import parse_condition

def test_func_cond():

    @FuncCond(syntax="is foo")
    def is_foo():
        return True

    cond = parse_condition("is foo")
    assert isinstance(cond, BaseCondition)
    assert bool(cond)

def test_func_cond_with_kwargs():

    @FuncCond(syntax=re.compile("is foo (?P<myval>true|false)"))
    def is_foo(myval):
        return True if myval == "true" else False if myval == "false" else None

    cond_true = parse_condition("is foo true")
    assert isinstance(cond_true, BaseCondition)
    assert bool(cond_true)

    cond_false = parse_condition("is foo false")
    assert isinstance(cond_false, BaseCondition)
    assert not bool(cond_false)

    assert cond_true is not cond_false

def test_func_cond_pass():

    @FuncCond()
    def is_foo(myval):
        return True if myval == "true" else False if myval == "false" else None

    # Test cond API
    cond = is_foo(myval="true")
    assert cond.kwargs == {"myval": "true"}

    cond = is_foo("true")
    assert cond.args == ("true",)

    assert is_foo(myval="true").observe()
    assert is_foo("true").observe()
    assert not is_foo(myval="false").observe()
    assert not is_foo("false").observe()

def test_func_cond_fail():
    cond = FuncCond()
    with pytest.raises(ValueError):
        # Has no func specified so should fail
        cond(value="asd")
