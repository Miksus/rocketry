import pytest

from rocketry.conditions import (
    TaskStarted,

    TaskFinished,
    TaskFailed,
    TaskSucceeded,

    TaskRunning
)
from rocketry.conditions.task import TaskInacted, TaskTerminated
from rocketry.core.task import TaskRun
from rocketry.pybox.time.convert import to_datetime, to_timestamp
from rocketry.time import (
    TimeOfDay
)
from rocketry.tasks import FuncTask

from .test_time import setup_task_state


@pytest.mark.parametrize("cls",
    [
        TaskFailed, TaskSucceeded, TaskFinished, TaskRunning, TaskStarted, TaskInacted, TaskTerminated
    ]
)
def test_logs_not_used_false(session, cls, mock_datetime_now):
    session.config.force_status_from_logs = False

    task = FuncTask(
        lambda:None,
        name="the task",
        execution="main",
        session=session
    )
    logs = [
        ("2021-01-01 12:00:00", state)
        for state in ("success", "fail", "run", "terminate", "inaction")
    ]
    setup_task_state(mock_datetime_now, logs, task=task)
    cond = cls(task=task)
    assert not cond.observe(session=session)

@pytest.mark.parametrize("cls",
    [
        TaskFailed, TaskSucceeded, TaskFinished, TaskRunning, TaskStarted, TaskInacted, TaskTerminated
    ]
)
def test_logs_not_used_true(session, cls, mock_datetime_now):
    session.config.force_status_from_logs = False

    task = FuncTask(
        lambda:None,
        name="the task",
        execution="main",
        session=session
    )
    for attr in ("_last_run", "_last_success", "_last_fail", "_last_inaction", "_last_terminate"):
        setattr(task, attr, to_datetime("2000-01-01 12:00:00").timestamp())
    if cls == TaskRunning:
        task.status = "run"
        run = TaskRun(start=1600000000, task=None)
        assert run.is_alive()
        task._run_stack.append(run)
    cond = cls(task=task)
    assert cond.observe(session=session)

@pytest.mark.parametrize("cls",
    [
        TaskFailed, TaskSucceeded, TaskFinished, TaskRunning, TaskStarted, TaskInacted, TaskTerminated
    ]
)
def test_logs_not_used_true_inside_period(session, cls, mock_datetime_now):
    session.config.force_status_from_logs = False

    task = FuncTask(
        lambda:None,
        name="the task",
        execution="main",
        session=session
    )
    for attr in ("_last_run", "_last_success", "_last_fail", "_last_inaction", "_last_terminate"):
        setattr(task, attr, to_datetime("2000-01-01 12:00:00").timestamp())

    cond = cls(task=task)
    cond = cls(task=task, period=TimeOfDay("07:00", "13:00"))
    if cls == TaskRunning:
        task.status = "run"
        run = TaskRun(start=to_timestamp(to_datetime("2000-01-01 12:00:00")), task=None)
        assert run.is_alive()
        task._run_stack.append(run)
    mock_datetime_now("2000-01-01 14:00")
    assert cond.observe(session=session)

@pytest.mark.parametrize("cls",
    [
        TaskFailed, TaskSucceeded, TaskFinished, TaskStarted, TaskInacted, TaskTerminated, TaskRunning
    ]
)
def test_logs_not_used_false_outside_period(session, cls, mock_datetime_now):
    session.config.force_status_from_logs = False

    task = FuncTask(
        lambda:None,
        name="the task",
        execution="main",
        session=session
    )
    for attr in ("_last_run", "_last_success", "_last_fail", "_last_inaction", "_last_terminate"):
        setattr(task, attr, to_datetime("2000-01-01 05:00:00").timestamp())
    cond = cls(task=task, period=TimeOfDay("07:00", "13:00"))
    mock_datetime_now("2000-01-01 14:00")
    if cls == TaskRunning:
        task.status = "run"
    assert not cond.observe(session=session)

@pytest.mark.parametrize("cls",
    [
        TaskFailed, TaskSucceeded, TaskFinished, TaskStarted, TaskInacted, TaskTerminated
    ]
)
def test_logs_not_used_equal_zero(session, cls, mock_datetime_now):
    session.config.force_status_from_logs = False

    task = FuncTask(
        lambda:None,
        name="the task",
        execution="main",
        session=session
    )
    logs = [
        ("2021-01-01 12:00:00", state)
        for state in ("success", "fail", "run", "terminate", "inaction")
    ]
    setup_task_state(mock_datetime_now, logs, task=task)
    cond = cls(task=task) == 0
    assert cond.observe(session=session)

@pytest.mark.parametrize("cls",
    [
        TaskFailed, TaskSucceeded, TaskFinished, TaskStarted, TaskInacted, TaskTerminated
    ]
)
def test_logs_used(session, cls, mock_datetime_now):
    session.config.force_status_from_logs = False

    task = FuncTask(
        lambda:None,
        name="the task",
        execution="main",
        session=session
    )
    logs = [
        ("2021-01-01 12:00:00", state)
        for state in ("success", "fail", "run", "terminate", "inaction")
    ]
    setup_task_state(mock_datetime_now, logs, task=task)
    # Only the latest status is stored
    # thus one cannot determine whether the task has run percisely once
    # without looking to logs.
    mock_datetime_now("2021-01-01 14:00")
    if cls is TaskFinished:
        cond = cls(task=task) == 3
    else:
        cond = cls(task=task) == 1
    assert cond.observe(session=session)
