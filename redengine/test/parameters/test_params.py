from redengine.core import Parameters
from redengine.core.parameters import Argument, Private
from redengine.parameters import Private

import pytest

@pytest.mark.parametrize(
    "get_param,mater,repr",
    [
        pytest.param(
            lambda: Parameters({"x": 0, "y": 1}),
            {"x": 0, "y": 1},
            {"x": 0, "y": 1},
            id="Dict"),
        pytest.param(
            lambda: Parameters(x=0, y=1),
            {"x": 0, "y": 1},
            {"x": 0, "y": 1},
            id="Kwargs"),
        pytest.param(
            lambda: Parameters(password="pwd1234", user_id="myself", type_=Private),
            {"password": "pwd1234", "user_id": "myself"},
            {"password": "*****", "user_id": "*****"},
            id="Dict as private"),
    ],
)
def test_contruct(get_param, mater, repr):
    params = get_param()
    assert mater == params.materialize()
    assert repr == params.represent()
    assert repr == dict(**params)


@pytest.mark.parametrize(
    "a,b,union",
    [
        pytest.param(
            lambda: Parameters({"a": 0, "b": 1}),
            lambda: Parameters({"c": 3, "d": 4}),
            lambda: Parameters({"a": 0, "b": 1, "c": 3, "d": 4}),
            id="Parameters | Parameters"),
        pytest.param(
            lambda: Parameters({"a": 0, "b": Private(1)}),
            lambda: Parameters({"c": 3, "d": Private(4)}),
            lambda: Parameters({"a": 0, "b": Private(1), "c": 3, "d": Private(4)}),
            id="Parameters | Parameters, with private"),
        pytest.param(
            lambda: Parameters({"a": 0, "b": 1}),
            lambda: {"c": 3, "d": 4},
            lambda: Parameters({"a": 0, "b": 1, "c": 3, "d": 4}),
            id="Parameters | Dict"),
        pytest.param(
            lambda: {"c": 3, "d": 4},
            lambda: Parameters({"a": 0, "b": 1}),
            lambda: Parameters({"a": 0, "b": 1, "c": 3, "d": 4}),
            id="Dict | Parameters", marks=pytest.mark.xfail),
    ],
)
def test_union(a, b, union):
    a = a()
    b = b()
    union = union()
    actual_union = a | b
    assert union == actual_union


@pytest.mark.parametrize(
    "a,b,union",
    [
        pytest.param(
            lambda: Parameters({"a": 0, "b": 1}),
            lambda: Parameters({"c": 3, "d": 4}),
            lambda: Parameters({"a": 0, "b": 1, "c": 3, "d": 4}),
            id="Parameters | Parameters"),
        pytest.param(
            lambda: Parameters({"a": 0, "b": Private(1)}),
            lambda: Parameters({"c": 3, "d": Private(4)}),
            lambda: Parameters({"a": 0, "b": Private(1), "c": 3, "d": Private(4)}),
            id="Parameters | Parameters, with private"),
        pytest.param(
            lambda: Parameters({"a": 0, "b": 1}),
            lambda: {"c": 3, "d": 4},
            lambda: Parameters({"a": 0, "b": 1, "c": 3, "d": 4}),
            id="Parameters | Dict"),
        pytest.param(
            lambda: {"c": 3, "d": 4},
            lambda: Parameters({"a": 0, "b": 1}),
            lambda: Parameters({"a": 0, "b": 1, "c": 3, "d": 4}),
            id="Dict | Parameters", marks=pytest.mark.xfail),
    ],
)
def test_update(a, b, union):
    a = a()
    b = b()
    union = union()
    a.update(b)
    assert union.materialize() == a.materialize()