
import pytest

from atlas.core import Scheduler
from atlas.task import FuncTask
from atlas.core.task.base import Task
from atlas.conditions import AlwaysFalse, AlwaysTrue, DependSuccess, Any, Not
from atlas import session

def test_construct(tmpdir):
    session.reset()
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = FuncTask(
            lambda : None,
        )
        assert task.status is None

def test_construct_decorate(tmpdir):
    session.reset()
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        session.reset()

        @FuncTask.decorate(start_cond=AlwaysTrue(), name="mytask")
        def do_stuff():
            pass
        
        assert isinstance(do_stuff, FuncTask)
        assert do_stuff.status is None
        assert do_stuff.start_cond == AlwaysTrue()
        assert do_stuff.name == "mytask"

        assert {"mytask": do_stuff} == session.tasks 


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
def test_set_start_condition(tmpdir, start_cond, depend, expected):

    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        session.reset()
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
def test_set_start_condition_str(tmpdir, start_cond_str, start_cond):

    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = FuncTask(
            lambda : None, 
            name="task",
            start_cond=start_cond_str
        )
        assert start_cond() == task.start_cond

        assert str(task.start_cond) == start_cond_str