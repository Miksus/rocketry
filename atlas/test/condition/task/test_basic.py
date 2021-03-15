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
            name="runned task",
            execution="main"
        )

        # Has not yet ran
        assert not bool(condition)

        # Now has
        try:
            task(params={"fail": not succeeding})
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
            name="prerequisite task",
            execution="main"
        )

        task = FuncTask(
            run_task, 
            name="runned task",
            execution="main"
        )

        # ------------------------ t0
        assert not bool(condition)


        # depend_task
        # -----|------------------- t0
        try: depend_task(params={"fail": True})
        except: pass
        assert bool(condition) if expected else not bool(condition)


        # depend_task     task
        # -----|-----------|------- t0
        task()
        assert not bool(condition)


        # depend_task     task     depend_task
        # -----|-----------|-----------|----------- t0
        try: depend_task(params={"fail": True})
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
            name="prerequisite task",
            execution="main"
        )

        task = FuncTask(
            run_task, 
            name="runned task",
            execution="main"
        )

        # ------------------------ t0
        assert not bool(condition)


        # depend_task
        # -----|------------------- t0
        depend_task(params={"fail": False})
        assert bool(condition) if expected else not bool(condition)


        # depend_task     task
        # -----|-----------|------- t0
        task()
        assert not bool(condition)


        # depend_task     task     depend_task
        # -----|-----------|-----------|----------- t0
        depend_task(params={"fail": False})
        assert bool(condition) if expected else not bool(condition)


        # depend_task     task     depend_task     task
        # -----|-----------|-----------|------------|-------- t0
        task()
        assert not bool(condition)


