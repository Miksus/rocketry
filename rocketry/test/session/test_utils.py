from rocketry.conditions.task import DependFailure, DependSuccess
from rocketry.core.condition.base import All, Any
from rocketry.tasks import FuncTask
from rocketry.utils.dependencies import Dependencies, Link, get_dependencies

def test_dependency(session):
    ta = FuncTask(lambda: None, name="a", start_cond="daily", execution="main", session=session)
    tb = FuncTask(lambda: None, name="b", start_cond="after task 'a'", execution="main", session=session)
    tc = FuncTask(lambda: None, name="c", start_cond="after task 'a' & after task 'b' failed", execution="main", session=session)
    td = FuncTask(lambda: None, name="d", start_cond="after task 'a' | after task 'b'", execution="main", session=session)

    te = FuncTask(lambda: None, name="no link", start_cond="daily", execution="main", session=session)

    # Test Dependencies
    # -----------------
    deps = Dependencies(session)
    deps_list = sorted(deps, key=lambda x: (x.child.name, x.parent.name))
    assert list(deps_list) == [
        Link(ta, tb, relation=DependSuccess),
        Link(ta, tc, relation=DependSuccess, type=All),
        Link(tb, tc, relation=DependFailure, type=All),
        Link(ta, td, relation=DependSuccess, type=Any),
        Link(tb, td, relation=DependSuccess, type=Any),
    ]
    assert str(deps)
    assert repr(deps)

    # Test get_dependencies
    # ---------------------
    deps = get_dependencies(session)
    deps_list = sorted(deps, key=lambda x: (x.child.name, x.parent.name))
    assert deps_list == [
        Link(ta, tb, relation=DependSuccess),
        Link(ta, tc, relation=DependSuccess, type=All),
        Link(tb, tc, relation=DependFailure, type=All),
        Link(ta, td, relation=DependSuccess, type=Any),
        Link(tb, td, relation=DependSuccess, type=Any),
    ]

def test_link(session):
    ta = FuncTask(lambda: None, name="a", start_cond="daily", execution="main", session=session)
    tb = FuncTask(lambda: None, name="b", start_cond="after task 'a'", execution="main", session=session)
    tc = FuncTask(lambda: None, name="c", start_cond="after task 'a' & after task 'b' failed", execution="main", session=session)
    td = FuncTask(lambda: None, name="d", start_cond="after task 'a' | after task 'b'", execution="main", session=session)

    assert str(Link(ta, tb, relation=DependSuccess)) == "'a' -> 'b'"
    assert str(Link(ta, tb, relation=DependFailure)) == "'a' -> 'b'"
    assert str(Link(ta, tb, relation=DependSuccess, type=Any)) == "'a' -> 'b'"
    assert str(Link(ta, tb, relation=DependSuccess, type=All)) == "'a' -> 'b' (multi)"

    assert repr(Link(ta, tb, relation=DependSuccess, type=All)) == "Link('a', 'b', relation=DependSuccess, type=All)"
