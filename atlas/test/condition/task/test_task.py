from atlas.conditions import (
    TaskStarted, 

    TaskFinished, 
    TaskFailed, 
    TaskSucceeded,

    TaskExecutable,

    DependFinish,
    DependFailure,
    DependSuccess
)
from atlas.time import (
    TimeDelta, 
    TimeOfDay
)

from atlas.core.task import Task
from atlas.core.conditions import set_statement_defaults
from atlas import session
from atlas.core import Scheduler
from atlas.task import FuncTask

import pytest
import pandas as pd
from dateutil.tz import tzlocal

import logging
import time

Task.use_instance_naming = True

def run_task(fail=False):
    print("Running func")
    if fail:
        raise RuntimeError("Task failed")

@pytest.mark.parametrize(
    "cls,succeeding,expected",
    [
        pytest.param(
            TaskFinished, True, 
            True,
            id="TaskFinished Success"),
        pytest.param(
            TaskFinished, False, 
            True,
            id="TaskFinished Failure"),

        pytest.param(
            TaskSucceeded, True, 
            True,
            id="TaskSucceeded Success"),
        pytest.param(
            TaskSucceeded, False, 
            False,
            id="TaskSucceeded Failure"),

        pytest.param(
            TaskFailed, True, 
            False,
            id="TaskFailed Success"),
        pytest.param(
            TaskFailed, False, 
            True,
            id="TaskFailed Failure"),
    ],
)
def test_task_status(tmpdir, cls, succeeding, expected):
    # Going to tempdir to dump the log files there

    with tmpdir.as_cwd() as old_dir:
        session.reset()
        condition = cls(task="runned task")

        task = FuncTask(
            run_task, 
            name="runned task"
        )

        # Has not yet ran
        assert not bool(condition)

        # Now has
        try:
            task(fail=not succeeding)
        except: 
            pass
        assert bool(condition) if expected else not bool(condition)


@pytest.mark.parametrize(
    "cls,expected",
    [
        pytest.param(
            DependFinish, 
            True,
            id="DependFinish"),

        pytest.param(
            DependSuccess, 
            False,
            id="DependSuccess"),

        pytest.param(
            DependFailure, 
            True,
            id="DependFailure"),
    ],
)
def test_task_depend_fail(tmpdir, cls, expected):
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        condition = cls(task="runned task", depend_task="prerequisite task")

        depend_task = FuncTask(
            run_task, 
            name="prerequisite task"
        )

        task = FuncTask(
            run_task, 
            name="runned task"
        )

        # ------------------------ t0
        assert not bool(condition)


        # depend_task
        # -----|------------------- t0
        try: depend_task(fail=True)
        except: pass
        assert bool(condition) if expected else not bool(condition)


        # depend_task     task
        # -----|-----------|------- t0
        task()
        assert not bool(condition)


        # depend_task     task     depend_task
        # -----|-----------|-----------|----------- t0
        try: depend_task(fail=True)
        except: pass
        assert bool(condition) if expected else not bool(condition)


        # depend_task     task     depend_task     task
        # -----|-----------|-----------|------------|-------- t0
        task()
        assert not bool(condition)


@pytest.mark.parametrize(
    "cls,expected",
    [
        pytest.param(
            DependFinish, 
            True,
            id="DependFinish"),

        pytest.param(
            DependSuccess, 
            True,
            id="DependSuccess"),

        pytest.param(
            DependFailure, 
            False,
            id="DependFailure"),
    ],
)
def test_task_depend_success(tmpdir, cls, expected):
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        condition = cls(task="runned task", depend_task="prerequisite task")

        depend_task = FuncTask(
            run_task, 
            name="prerequisite task"
        )

        task = FuncTask(
            run_task, 
            name="runned task"
        )

        # ------------------------ t0
        assert not bool(condition)


        # depend_task
        # -----|------------------- t0
        depend_task(fail=False)
        assert bool(condition) if expected else not bool(condition)


        # depend_task     task
        # -----|-----------|------- t0
        task()
        assert not bool(condition)


        # depend_task     task     depend_task
        # -----|-----------|-----------|----------- t0
        depend_task(fail=False)
        assert bool(condition) if expected else not bool(condition)


        # depend_task     task     depend_task     task
        # -----|-----------|-----------|------------|-------- t0
        task()
        assert not bool(condition)


@pytest.mark.parametrize(
    "get_condition,logs,time_after,outcome",
    [
        pytest.param(
            lambda:TaskExecutable(task="the task", period=TimeOfDay("07:00", "08:00")), 
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "success"),
            ],
            "2020-01-01 07:30",
            False,
            id="Don't run (already succeeded)"),

        pytest.param(
            lambda:TaskExecutable(task="the task", period=TimeOfDay("07:00", "08:00")), 
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "fail"),
            ],
            "2020-01-01 07:30",
            False,
            id="Don't run (already failed)"),
    
        pytest.param(
            lambda:TaskExecutable(task="the task", period=TimeOfDay("07:00", "08:00")), 
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "terminate"),
            ],
            "2020-01-01 07:30",
            False,
            id="Don't run (terminated)"),
    
        pytest.param(
            # Termination is kind of failing but retry is not applicable as termination is often
            # indication that the task is not desired to be run anymore (as it has already taken
            # enough system resources)
            lambda:TaskExecutable(task="the task", period=TimeOfDay("07:00", "08:00"), retries=1), 
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "terminate"),
            ],
            "2020-01-01 07:30",
            False,
            id="Don't run (terminated with retries)"),

        pytest.param(
            lambda:TaskExecutable(task="the task", period=TimeOfDay("07:00", "08:00")), 
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "success"),
            ],
            "2020-01-01 08:30",
            False,
            id="Don't run (already ran and out of time)"),

        pytest.param(
            lambda:TaskExecutable(task="the task", period=TimeOfDay("07:00", "08:00")), 
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "success"),
            ],
            "2021-12-31 08:30",
            False,
            id="Don't run (missed)"),

        pytest.param(
            lambda:TaskExecutable(task="the task", period=TimeOfDay("07:00", "08:00")), 
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "success"),
            ],
            "2021-12-31 06:00",
            False,
            id="Don't run (not yet time)"),

        pytest.param(
            lambda:TaskExecutable(task="the task", period=TimeOfDay("07:00", "08:00")), 
            [],
            "2020-01-01 08:30",
            False,
            id="Don't run (out of time and not run at all)"),

        # Do run
        pytest.param(
            lambda:TaskExecutable(task="the task", period=TimeOfDay("07:00", "08:00")), 
            [],
            "2020-01-01 07:10",
            True,
            id="Do run (has not run at all)"),
        pytest.param(
            lambda:TaskExecutable(task="the task", period=TimeOfDay("07:00", "08:00"), retries=1), 
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "fail"),
            ],
            "2020-01-01 07:30",
            True,
            id="Do run (has retries)"),

        pytest.param(
            lambda:TaskExecutable(task="the task", period=TimeOfDay("07:00", "08:00")), 
            [
                ("2020-01-01 07:10", "run"),
                ("2020-01-01 07:20", "inaction"),
            ],
            "2020-01-01 07:30",
            True,
            id="Do run (has inacted)"),
    ],
)
def test_task_executable(tmpdir, mock_datetime_now, logs, time_after, get_condition, outcome):

    def to_epoch(dt):
        # Hack as time.tzlocal() does not work for 1970-01-01
        if dt.tz:
            dt = dt.tz_convert("utc").tz_localize(None)
        return (dt - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')

    with tmpdir.as_cwd() as old_dir:
        session.reset()

        
        task = FuncTask(
            run_task, 
            name="the task"
        )

        condition = get_condition()

        # pd.Timestamp -> Epoch, https://stackoverflow.com/a/54313505/13696660
        # We also need tz_localize to convert timestamp to localized form (logging thinks the time is local time and convert that to GTM)

        for log in logs:
            log_time, log_action = log[0], log[1]
            log_created = to_epoch(pd.Timestamp(log_time, tz=tzlocal()))
            record = logging.LogRecord(
                # The content here should not matter for task status
                name='atlas.core.task.base', level=logging.INFO, lineno=1, 
                pathname='d:\\Projects\\atlas\\atlas\\core\\task\\base.py',
                msg="Logging of 'task'", args=(), exc_info=None,
            )

            record.created = log_created
            record.action = log_action
            record.task_name = "the task"

            task.logger.handle(record)
        mock_datetime_now(time_after)

        if outcome:
            assert bool(condition) 
        else:
            assert not bool(condition)
