
import pytest
from textwrap import dedent

from redengine.conditions.task import DependFailure, DependFinish, DependSuccess
from redengine.core.condition.base import All, Any
from redengine.tasks import FuncTask
from redengine import Session
from redengine.views.dependency import Link

def test_dependency(session):
    ta = FuncTask(lambda: None, name="a", start_cond="daily", execution="main")
    tb = FuncTask(lambda: None, name="b", start_cond="after task 'a'", execution="main")
    tc = FuncTask(lambda: None, name="c", start_cond="after task 'a' & after task 'b' failed", execution="main")
    td = FuncTask(lambda: None, name="d", start_cond="after task 'a' | after task 'b'", execution="main")

    te = FuncTask(lambda: None, name="no link", start_cond="daily", execution="main")

    deps = session.dependencies
    assert list(deps) == [
        Link(ta, tb, relation=DependSuccess),
        Link(ta, tc, relation=DependSuccess, type=All),
        Link(tb, tc, relation=DependFailure, type=All),
        Link(ta, td, relation=DependSuccess, type=Any),
        Link(tb, td, relation=DependSuccess, type=Any),
    ]
    assert str(deps) == dedent("""
    'a' -> 'b'
    'a' -> 'c' (multi)
    'b' -> 'c' (multi)
    'a' -> 'd'
    'b' -> 'd'
    """)[1:-1]

    assert deps.to_dict() == [
        {'parent': ta, 'child': tb, "relation": DependSuccess, "type": None},
        {'parent': ta, 'child': tc, "relation": DependSuccess, "type": All},
        {'parent': tb, 'child': tc, "relation": DependFailure, "type": All},
        {'parent': ta, 'child': td, "relation": DependSuccess, "type": Any},
        {'parent': tb, 'child': td, "relation": DependSuccess, "type": Any},
    ]

def test_networkx_no_error(session):
    ta = FuncTask(lambda: None, name="first", start_cond="daily", execution="main")
    tb = FuncTask(lambda: None, name="b", start_cond="after task 'first'", execution="main")
    tc = FuncTask(lambda: None, name="c", start_cond="after task 'first' & after task 'b' failed", execution="main")
    td = FuncTask(lambda: None, name="d", start_cond="after task 'first' | after task 'b'", execution="main")

    te = FuncTask(lambda: None, name="no link", start_cond="daily", execution="main")

    pytest.importorskip('networkx')
    G = session.dependencies.to_networkx()
    
    # import matplotlib.pyplot as plt
    # plt.show()
    pass