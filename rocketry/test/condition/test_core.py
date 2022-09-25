
import pytest

from rocketry.conditions import (
    ParamExists, IsPeriod,
    Any, All, Not
)
from rocketry.conds import true, false
from rocketry.time import TimeDelta, always

def test_true():
    assert bool(true)

def test_false():
    assert not bool(false)

@pytest.mark.parametrize(
    "params,make_cond,expected",
    [
        pytest.param(
            {"mode": "test", "state": "right"},
            lambda: ParamExists(mode="test", state="right"),
            True, id="Dict, true"
        ),
        pytest.param(
            {"mode": "test", "state": "right"},
            lambda: ParamExists(mode="test", state="wrong"),
            False, id="Dict, false (wrong value)"
        ),
        pytest.param(
            {"mode": "test", "state": "right"},
            lambda: ParamExists(mode="test", stuff="right"),
            False, id="Dict, false (missing key)"
        ),
        pytest.param(
            {"mode": "test", "state": "right"},
            lambda: ParamExists("mode"),
            True, id="Tuple, true"
        ),
        pytest.param(
            {"mode": "test", "state": "right"},
            lambda: ParamExists("stuff"),
            False, id="Tuple, false (missing key)"
        ),
        pytest.param(
            {"mode": "test", "feel": "good", "state": "right", "distance": "short", "world": "this"},
            lambda: ParamExists("mode", "feel", state="right", distance="short"),
            True, id="Multi, true"
        ),
        pytest.param(
            {},
            lambda: ParamExists("mode", "feel", state="right", distance="short"),
            False, id="Multi, false (empty)"
        ),
    ]
)
def test_params(session, params, make_cond, expected):

    session.parameters.update(params)
    cond = make_cond()
    if expected:
        assert bool(cond)
    else:
        assert not bool(cond)

def test_parameter_exists(session):
    cond = ParamExists(x="yes", y="yes")
    assert not bool(cond)

    session.parameters["x"] = "yes"
    assert not bool(cond)

    session.parameters["y"] = "yes"
    assert bool(cond)

    session.parameters["y"] = "no"
    assert not bool(cond)


@pytest.mark.parametrize("get_cond,exc",
    [
        pytest.param(lambda: IsPeriod(TimeDelta("2 hours")), AttributeError, id="IsPeriod with timedelta")
    ]
)
def test_fail(get_cond,exc):
    with pytest.raises(exc):
        get_cond()

@pytest.mark.parametrize("obj,string,represent",
    [
        pytest.param(
            All(true, false),
            "(true & false)",
            "All(true, false)",
            id="All"),
        pytest.param(
            Any(true, false),
            "(true | false)",
            "Any(true, false)",
            id="Any"),
        pytest.param(
            IsPeriod(always),
            "currently always",
            "IsPeriod(period=always)",
            id="IsPeriod"),
        pytest.param(
            Not(true),
            "~true",
            "Not(true)",
            id="Not"),
    ]
)
def test_representation(obj, string, represent):
    assert str(obj) == string
    assert repr(obj) == represent

def test_logic():
    assert list(All(true, true, false)) == [true, true, false]
    assert list(Any(true, true, false)) == [true, true, false]

    assert All(true, true, false)[2] is false
    assert Any(true, true, false)[2] is false

    assert Not(true) == false
    assert Not(true) != true

    assert Not(false) == true
    assert Not(false) != false

    assert Not(false) != "invalid"
