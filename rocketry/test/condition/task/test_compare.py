from time import time
import pytest
from rocketry.conditions import (
    TaskFinished, TaskRunning
)
from rocketry.core.task import TaskRun
from rocketry.core.time.base import TimeDelta
from rocketry.tasks import FuncTask
from rocketry.log import MinimalRunRecord

def run_task(fail=False):
    print("Running func")
    if fail:
        raise RuntimeError("Task failed")

def test_task_finish_compare(tmpdir, session):
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd():
        equals = TaskFinished(task="runned task") == 2
        greater = TaskFinished(task="runned task") > 2
        less = TaskFinished(task="runned task") < 2

        task = FuncTask(
            run_task,
            name="runned task",
            execution="main",
            session=session
        )

        # Has not yet ran
        assert not bool(equals.observe(session=session))
        assert not bool(greater.observe(session=session))
        assert bool(less.observe(session=session))

        task()
        task()

        assert bool(equals.observe(session=session))
        assert not bool(greater.observe(session=session))
        assert not bool(less.observe(session=session))

        task()
        assert not bool(equals.observe(session=session))
        assert bool(greater.observe(session=session))
        assert not bool(less.observe(session=session))

@pytest.mark.parametrize("how", ["stack", "logs", "logs with run_id"])
def test_running(tmpdir, session, how):
    if how == 'logs':
        session.config.force_status_from_logs = True
    if how == 'logs with run_id':
        session.config.force_status_from_logs = True
        repo = session.get_repo()
        repo.model = MinimalRunRecord

    # Going to tempdir to dump the log files there
    equals = TaskRunning(task="runned task") == 2
    greater = TaskRunning(task="runned task") > 2
    less = TaskRunning(task="runned task") < 2

    equals_inside = TaskRunning(task="runned task", period=TimeDelta("2 hours")) == 2
    equals_outside = TaskRunning(task="runned task", period=TimeDelta("0 seconds")) == 2

    task = FuncTask(
        run_task,
        name="runned task",
        execution="main",
        session=session
    )

    # Has not yet ran
    assert not bool(equals.observe(session=session))
    assert not bool(greater.observe(session=session))
    assert bool(less.observe(session=session))

    assert not bool(equals_inside.observe(session=session))
    assert not bool(equals_outside.observe(session=session))

    if how == "stack":
        task._run_stack.append(TaskRun(start=time(), task=None))
    else:
        task.log_running()

    # Has run once
    assert not bool(equals.observe(session=session))
    assert not bool(greater.observe(session=session))
    assert bool(less.observe(session=session))

    assert not bool(equals_inside.observe(session=session))
    assert not bool(equals_outside.observe(session=session))


    if how == "stack":
        task._run_stack.append(TaskRun(start=time(), task=None))
    else:
        task.log_running()

    # Has run two times
    assert bool(equals.observe(session=session))
    assert not bool(greater.observe(session=session))
    assert not bool(less.observe(session=session))

    assert bool(equals_inside.observe(session=session))
    assert not bool(equals_outside.observe(session=session))

    if how == "stack":
        task._run_stack.append(TaskRun(start=time(), task=None))
    else:
        task.log_running()

    # Has run three times
    assert not bool(equals.observe(session=session))
    assert bool(greater.observe(session=session))
    assert not bool(less.observe(session=session))

    assert not bool(equals_inside.observe(session=session))
    assert not bool(equals_outside.observe(session=session))
