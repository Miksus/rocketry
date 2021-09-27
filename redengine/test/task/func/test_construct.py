
import types

import pytest

from redengine.tasks import FuncTask
from redengine.conditions import AlwaysFalse, AlwaysTrue, DependSuccess

def test_construct(tmpdir, session):

    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:

        task = FuncTask(
            lambda : None,
        )
        assert task.status is None

def test_construct_decorate(tmpdir, session):
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:


        @FuncTask(start_cond=AlwaysTrue(), name="mytask")
        def do_stuff():
            pass
        
        assert isinstance(do_stuff, types.FunctionType)

        do_stuff_task = session.tasks["mytask"]
        assert isinstance(do_stuff_task, FuncTask)
        assert do_stuff_task.status is None
        assert do_stuff_task.start_cond == AlwaysTrue()
        assert do_stuff_task.name == "mytask"

        assert {"mytask": do_stuff_task} == session.tasks 

def test_construct_decorate_minimal(tmpdir, session):
    """This is an exception when FuncTask returns itself 
    (__init__ cannot return anything else)"""
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:

        @FuncTask
        def do_stuff():
            pass

        assert isinstance(do_stuff, FuncTask)
        assert do_stuff.status is None
        assert do_stuff.start_cond == AlwaysFalse()
        assert do_stuff.name.endswith(":do_stuff")

        assert [do_stuff] == list(session.tasks.values())

def test_construct_decorate_default_name(tmpdir, session):
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:


        @FuncTask(start_cond=AlwaysTrue())
        def do_stuff():
            pass
        
        assert isinstance(do_stuff, types.FunctionType)
        do_stuff_task = list(session.tasks.values())[-1]
        assert isinstance(do_stuff_task, FuncTask)
        assert do_stuff_task.status is None
        assert do_stuff_task.start_cond == AlwaysTrue()
        assert do_stuff_task.name.endswith(":do_stuff")

        assert [do_stuff_task] == list(session.tasks.values())

@pytest.mark.parametrize(
    "start_cond,depend,expected",
    [
        pytest.param(
            AlwaysTrue(),
            None,
            AlwaysTrue(),
            id="AlwaysTrue"),
        pytest.param(
            AlwaysTrue(),
            ["another task"],
            AlwaysTrue() & DependSuccess(task="task", depend_task="another task"),
            id="AlwaysTrue with dependent"),
    ],
)
def test_set_start_condition(tmpdir, start_cond, depend, expected, session):

    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:

        task = FuncTask(
            lambda : None, 
            name="task",
            start_cond=start_cond,
            dependent=depend
        )
        assert expected == task.start_cond


@pytest.mark.parametrize(
    "start_cond_str,start_cond",
    [
        pytest.param("true", lambda: AlwaysTrue(), id="true"),
        pytest.param("always true & always true", lambda: AlwaysTrue() & AlwaysTrue(), id="always true & always true"),
    ],
)
def test_set_start_condition_str(tmpdir, start_cond_str, start_cond, session):

    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:

        task = FuncTask(
            lambda : None, 
            name="task",
            start_cond=start_cond_str
        )
        assert start_cond() == task.start_cond

        assert str(task.start_cond) == start_cond_str