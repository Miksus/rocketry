
import pytest

from atlas.core import Scheduler
from atlas.task import FuncTask
from atlas.core.task.base import Task, get_task
from atlas.conditions import AlwaysFalse, AlwaysTrue, DependSuccess, Any
from atlas import session

def test_construct(tmpdir):
    session.reset()
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            lambda : None,
        )
        assert task.status is None


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


def test_set_start_condition_str(tmpdir):

    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = FuncTask(
            lambda : None, 
            name="task",
            start_cond="always true | always false"
        )
        assert isinstance(task.start_cond, Any)

        assert isinstance(task.start_cond[0], AlwaysTrue)
        assert isinstance(task.start_cond[1], AlwaysFalse)
        assert len(list(task.start_cond))