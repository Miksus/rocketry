import datetime

import pytest

from rocketry.conditions import (
    TaskRunnable,
)
from rocketry.pybox.time.convert import to_datetime
from rocketry.time import (
    TimeOfDay
)
from rocketry.tasks import FuncTask
from rocketry.testing.log import create_task_record

@pytest.mark.parametrize("from_logs", [pytest.param(True, id="from logs"), pytest.param(False, id="optimized")])
@pytest.mark.parametrize(
    "get_condition,logs,time_after,outcome",
    [
        pytest.param(
            lambda:TaskRunnable(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "success"),
            ],
            "2020-01-01 07:30",
            False,
            id="Don't run (already ran)"),

        pytest.param(
            lambda:TaskRunnable(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "success"),
            ],
            "2020-01-01 08:30",
            False,
            id="Don't run (already ran, out of the period)"),

        pytest.param(
            lambda:TaskRunnable(task="the task", period=TimeOfDay("07:00", "08:00")),
            [],
            "2020-01-01 08:30",
            False,
            id="Don't run (out of the period)"),

        pytest.param(
            lambda:TaskRunnable(task="the task", period=TimeOfDay("07:00", "08:00")),
            [],
            "2020-01-02 07:30",
            True,
            id="Do run (has not run)"),

        pytest.param(
            lambda:TaskRunnable(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "inaction"),
            ],
            "2020-01-02 07:30",
            True,
            id="Do run (ran yesterday)"),

        pytest.param(
            lambda:TaskRunnable(task="the task", period=TimeOfDay("07:00", "08:00")),
            [
                ("2020-01-01 06:50", "run"),
                ("2020-01-01 07:20", "success"),
            ],
            "2020-01-01 07:30",
            True,
            id="Do run (ran outside the period)"),

    ],
)
def test_runnable(tmpdir, mock_datetime_now, logs, time_after, get_condition, outcome, session, from_logs):
    session.config.force_status_from_logs = from_logs
    def to_epoch(dt):
        # Hack as time.tzlocal() does not work for 1970-01-01
        if dt.tz:
            dt = dt.tz_convert("utc").tz_localize(None)
        return (dt - datetime.datetime(1970,  1, 1)) // datetime.timedelta(seconds=1)

    with tmpdir.as_cwd():


        task = FuncTask(
            lambda:None,
            name="the task",
            execution="main",
            session=session
        )

        condition = get_condition()

        for log in logs:
            log_time, log_action = log[0], log[1]
            record = create_task_record(
                # The content here should not matter for task status
                name='rocketry.core.task', lineno=1,
                pathname='d:\\Projects\\rocketry\\rocketry\\core\\task\\base.py',
                msg="Logging of 'task'", args=(), exc_info=None,
                created=log_time, action=log_action, task_name="the task"
            )

            task.logger.handle(record)
            setattr(task, f'_last_{log_action}', to_datetime(log_time).timestamp())
        mock_datetime_now(time_after)

        if outcome:
            assert condition.observe(session=session)
            assert condition.observe(task=task)
        else:
            assert not condition.observe(session=session)
            assert not condition.observe(task=task)
