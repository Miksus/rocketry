from typing import List, Tuple

import pytest

from rocketry.conditions import (
    TaskStarted,

    TaskFinished,
    TaskFailed,
    TaskSucceeded,

    TaskRunning
)
from rocketry.testing.log import create_task_record
from rocketry.time import (
    TimeOfDay, TimeSpanDelta
)
from rocketry.tasks import FuncTask


def setup_task_state(mock_datetime_now, logs:List[Tuple[str, str]], time_after=None, task=None, session=None):
    """A mock up that sets up a task to test the
    condition with given logs

    Parameters
    ----------
    tmpdir : Pytest fixture
    mock_datetime_now : Pytest fixture
    logs : list of tuples
        Logs to be inserted for the task.
        The tuple is in form (datetime, action)
    time_after : date-like
        The datetime when inspecting the condition status
    """
    if task is None:
        task = FuncTask(
            lambda:None,
            name="the task",
            execution="main",
            session=session
        )

    for log in logs:
        log_time, log_action = log[0], log[1]
        record = create_task_record(
            created=log_time, action=log_action, task_name="the task",
            # The content here should not matter for task status
            pathname='rocketry\\rocketry\\core\\task\\base.py',
            msg="Logging of 'task'", args=(), exc_info=None,
        )

        task.logger.handle(record)

    if time_after is not None:
        mock_datetime_now(time_after)
    return task


@pytest.mark.parametrize(
    "get_condition,logs,time_after,outcome",
    [
        pytest.param(
            lambda:TaskRunning(task="the task"),
            [
                ("2020-01-01 07:10", "run"),
            ],
            "2020-01-01 07:30",
            True,
            id="Is running"),
        pytest.param(
            lambda:TaskRunning(task="the task"),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "run"),
            ],
            "2020-01-01 07:30",
            True,
            id="Is running (multiple times)"),

        pytest.param(
            lambda:TaskRunning(task="the task"),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:15", "success"),
            ],
            "2020-01-01 07:30",
            False,
            id="Is not running (succeeded)"),
        pytest.param(
            lambda:TaskRunning(task="the task"),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:15", "fail"),
            ],
            "2020-01-01 07:30",
            False,
            id="Is not running (failed)"),
        pytest.param(
            lambda:TaskRunning(task="the task"),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:15", "terminate"),
            ],
            "2020-01-01 07:30",
            False,
            id="Is not running (terminated)"),
        pytest.param(
            lambda:TaskRunning(task="the task"),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:15", "inaction"),
            ],
            "2020-01-01 07:30",
            False,
            id="Is not running (inacted)"),
        pytest.param(
            lambda:TaskRunning(task="the task"),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:15", "crash"),
            ],
            "2020-01-01 07:30",
            False,
            id="Is not running (crash_release)"),
        pytest.param(
            lambda:TaskRunning(task="the task"),
            [],
            "2020-01-01 07:30",
            False,
            id="Is not running (and has never ran)"),
        pytest.param(
            lambda:TaskRunning(task="the task"),
            [
                ("2020-01-01 07:50", "run"),
            ],
            "2020-01-01 07:30",
            False,
            id="Is not running (but does in the future)", marks=pytest.mark.xfail(reason="Bug but not likely to encounter")),

        pytest.param(
            lambda:TaskRunning(task="the task", period=TimeSpanDelta(far="2 hours")),
            [
                ("2020-01-01 07:10", "run"),
            ],
            "2020-01-01 07:30",
            True,
            id="Is running (with period)"),
        pytest.param(
            lambda:TaskRunning(task="the task", period=TimeSpanDelta(far="10 mins")),
            [
                ("2020-01-01 07:10", "run"),
            ],
            "2020-01-01 07:30",
            False,
            id="Is not running (with period, out of period)"),
        pytest.param(
            lambda:TaskRunning(task="the task", period=TimeSpanDelta(far="2 hours")),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:15", "success"),
            ],
            "2020-01-01 07:30",
            False,
            id="Is not running (with period, success)"),
    ],
)
def test_running(mock_datetime_now, logs, time_after, get_condition, outcome, session):
    session.config.force_status_from_logs = True
    task = setup_task_state(mock_datetime_now, logs, time_after, session=session)
    cond = get_condition()
    if outcome:
        assert cond.observe(session=session)
        assert cond.observe(task=session['the task'])
    else:
        assert not cond.observe(session=session)
        assert not cond.observe(task=session['the task'])


@pytest.mark.parametrize(
    "get_condition,logs,time_after,outcome",
    [
        pytest.param(
            lambda:TaskStarted(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
            ],
            "2020-01-01 07:30",
            True,
            id="Has started"),
        pytest.param(
            lambda:TaskStarted(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:12", "fail"),
                ("2020-01-01 07:12", "success"),
                ("2020-01-01 07:12", "inaction"),
                ("2020-01-01 07:12", "terminate"),
            ],
            "2020-01-01 07:30",
            True,
            id="Has started (also failed, succeeded, terminated & inacted)"),

        pytest.param(
            lambda:TaskStarted(task="the task", period=TimeOfDay("07:00", "08:00")),
            [],
            "2020-01-02 07:30",
            False,
            id="Not started (at all)"),
        pytest.param(
            lambda:TaskStarted(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:15", "run"),
            ],
            "2020-01-02 07:30",
            False,
            id="Not started (today)"),
        pytest.param(
            lambda:TaskStarted(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:12", "fail"),
                ("2020-01-01 07:12", "success"),
                ("2020-01-01 07:12", "inaction"),
                ("2020-01-01 07:12", "terminate"),
            ],
            "2020-01-01 07:30",
            False,
            id="Not started (but failed, succeeded, terminated & inacted)"),
    ],
)
def test_started(tmpdir, mock_datetime_now, logs, time_after, get_condition, outcome, session):
    session.config.force_status_from_logs = True
    setup_task_state(mock_datetime_now, logs, time_after, session=session)
    cond = get_condition()
    if outcome:
        assert cond.observe(session=session)
        assert cond.observe(task=session['the task'])
    else:
        assert not cond.observe(session=session)
        assert not cond.observe(task=session['the task'])



@pytest.mark.parametrize(
    "get_condition,logs,time_after,outcome",
    [
        pytest.param(
            lambda:TaskFinished(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "success"),
            ],
            "2020-01-01 07:30",
            True,
            id="Has finished (succeded)"),
        pytest.param(
            lambda:TaskFinished(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "fail"),
            ],
            "2020-01-01 07:30",
            True,
            id="Has finished (failed)"),
        pytest.param(
            lambda:TaskFinished(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "terminate"),
            ],
            "2020-01-01 07:30",
            True,
            id="Has finished (terminated)"),


        # Not
        pytest.param(
            lambda:TaskFinished(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
            ],
            "2020-01-01 07:30",
            False,
            id="Not finished (only started)"),
        pytest.param(
            lambda:TaskFinished(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "inaction"),
            ],
            "2020-01-01 07:30",
            False,
            id="Not finished (inacted)"),

        pytest.param(
            lambda:TaskFinished(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 00:10", "run"),
                ("2020-01-01 00:20", "success"),
            ],
            "2020-01-01 07:30",
            False,
            id="Not finished (success out of period)"),
        pytest.param(
            lambda:TaskFinished(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 00:10", "run"),
                ("2020-01-01 00:20", "fail"),
            ],
            "2020-01-01 07:30",
            False,
            id="Not finished (fail out of period)"),
        pytest.param(
            lambda:TaskFinished(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 00:10", "run"),
                ("2020-01-01 00:20", "terminate"),
            ],
            "2020-01-01 07:30",
            False,
            id="Not finished (termination out of period)"),
        pytest.param(
            lambda:TaskFinished(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 00:10", "run"),
                ("2020-01-01 00:20", "inaction"),
            ],
            "2020-01-01 07:30",
            False,
            id="Not finished (inaction out of period)"),
    ],
)
def test_finish(tmpdir, mock_datetime_now, logs, time_after, get_condition, outcome, session):
    session.config.force_status_from_logs = True
    setup_task_state(mock_datetime_now, logs, time_after, session=session)
    cond = get_condition()
    if outcome:
        assert cond.observe(session=session)
    else:
        assert not cond.observe(session=session)


@pytest.mark.parametrize(
    "get_condition,logs,time_after,outcome",
    [
        pytest.param(
            lambda:TaskSucceeded(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "success"),
            ],
            "2020-01-01 07:30",
            True,
            id="Has succeeded"),
        pytest.param(
            lambda:TaskSucceeded(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "success"),
                ("2020-01-01 07:30", "run"),
                ("2020-01-01 07:40", "success"),
            ],
            "2020-01-01 07:30",
            True,
            id="Has succeeded (multiple times)"),

        pytest.param(
            lambda:TaskSucceeded(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "success"),
                ("2020-01-01 07:40", "success"),
                ("2020-01-01 07:50", "success"),
            ],
            "2020-01-01 07:30",
            True,
            id="Has succeeded (multiple times oddly)"),

        # Not
        pytest.param(
            lambda:TaskSucceeded(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "success"),
                ("2020-01-02 07:10", "run"),
                ("2020-01-02 07:20", "success"),
            ],
            "2020-01-03 07:30",
            False,
            id="Not succeeded (today)"),
        pytest.param(
            lambda:TaskSucceeded(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
            ],
            "2020-01-01 07:30",
            False,
            id="Not succeeded (only started)"),
        pytest.param(
            lambda:TaskSucceeded(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "fail"),
            ],
            "2020-01-01 07:30",
            False,
            id="Not succeeded (only failed)"),
        pytest.param(
            lambda:TaskSucceeded(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "inaction"),
            ],
            "2020-01-01 07:30",
            False,
            id="Not succeeded (only inacted)"),
        pytest.param(
            lambda:TaskSucceeded(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "terminate"),
            ],
            "2020-01-01 07:30",
            False,
            id="Not succeeded (only terminated)"),

    ],
)
def test_success(tmpdir, mock_datetime_now, logs, time_after, get_condition, outcome, session):
    session.config.force_status_from_logs = True
    setup_task_state(mock_datetime_now, logs, time_after, session=session)
    cond = get_condition()
    if outcome:
        assert cond.observe(session=session)
    else:
        assert not cond.observe(session=session)


@pytest.mark.parametrize(
    "get_condition,logs,time_after,outcome",
    [
        pytest.param(
            lambda:TaskFailed(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "fail"),
            ],
            "2020-01-01 07:30",
            True,
            id="Has failed"),
        pytest.param(
            lambda:TaskFailed(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "fail"),
                ("2020-01-01 07:30", "run"),
                ("2020-01-01 07:40", "fail"),
            ],
            "2020-01-01 07:30",
            True,
            id="Has failed (multiple times)"),

        pytest.param(
            lambda:TaskFailed(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "fail"),
                ("2020-01-01 07:40", "fail"),
                ("2020-01-01 07:50", "fail"),
            ],
            "2020-01-01 07:30",
            True,
            id="Has failed (multiple times oddly)"),

        # Not
        pytest.param(
            lambda:TaskFailed(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "fail"),
                ("2020-01-02 07:10", "run"),
                ("2020-01-02 07:20", "fail"),
            ],
            "2020-01-03 07:30",
            False,
            id="Not failed (today)"),
        pytest.param(
            lambda:TaskFailed(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
            ],
            "2020-01-01 07:30",
            False,
            id="Not failed (only started)"),
        pytest.param(
            lambda:TaskFailed(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "success"),
            ],
            "2020-01-01 07:30",
            False,
            id="Not failed (only succeeded)"),
        pytest.param(
            lambda:TaskFailed(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "inaction"),
            ],
            "2020-01-01 07:30",
            False,
            id="Not failed (only inacted)"),
        pytest.param(
            lambda:TaskFailed(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "terminate"),
            ],
            "2020-01-01 07:30",
            False,
            id="Not failed (only terminated)"),

    ],
)
def test_fail(mock_datetime_now, logs, time_after, get_condition, outcome, session):
    session.config.force_status_from_logs = True
    setup_task_state(mock_datetime_now, logs, time_after, session=session)
    cond = get_condition()
    if outcome:
        assert cond.observe(session=session)
    else:
        assert not cond.observe(session=session)
