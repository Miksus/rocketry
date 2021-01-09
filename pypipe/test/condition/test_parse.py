
from pypipe.parse import parse_condition
from pypipe.conditions import (
    AlwaysTrue, AlwaysFalse, 
    All, Any, Not,
    TaskFailed, TaskFinished, TaskRunning, TaskStarted, TaskSucceeded,
)
import pytest

@pytest.mark.parametrize(
    "cond_str,expected",
    [
        pytest.param(
            "always true", 
            AlwaysTrue(),
            id="AlwaysTrue"),

        pytest.param(
            "always false", 
            AlwaysFalse(),
            id="AlwaysFalse"),

        pytest.param(
            "always true & always true", 
            AlwaysTrue() & AlwaysTrue(),
            id="All"),
        pytest.param(
            "always true | always true", 
            AlwaysTrue() | AlwaysTrue(),
            id="Any"),
        pytest.param(
            "~always true", 
            Not(AlwaysTrue()),
            id="Not"),

        pytest.param(
            "~~always true", 
            ~~AlwaysTrue(),
            id="Nested Not"),

        pytest.param(
            "~(always true)", 
            ~AlwaysTrue(),
            id="Closured Not"),

        pytest.param(
            "~(always true & always true)", 
            ~(AlwaysTrue() & AlwaysTrue()),
            id="All in Not"),

        pytest.param(
            "~(always true | always true)", 
            ~(AlwaysTrue() | AlwaysTrue()),
            id="Any in Not"),

        pytest.param(
            "~always true | ~always true", 
            ~AlwaysTrue() | ~AlwaysTrue(),
            id="Multiple Not"),

        pytest.param(
            "always true & (always true | always true & (always true | always true))", 
            AlwaysTrue() & (AlwaysTrue() | AlwaysTrue() & (AlwaysTrue() | AlwaysTrue())),
            id="Nested"),

        pytest.param(
            "", 
            AlwaysFalse(),
            id="Empty"),
    ],
)
def test_string(cond_str, expected):
    cond = parse_condition(cond_str)
    assert cond == expected