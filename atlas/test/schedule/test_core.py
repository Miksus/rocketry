
from atlas.core import Scheduler
from atlas.task import FuncTask
from atlas.time import TimeDelta
from atlas.core.task.base import Task
from atlas.core.exceptions import TaskInactionException
from atlas.conditions import SchedulerCycles, SchedulerStarted, TaskFinished, TaskStarted, AlwaysFalse, AlwaysTrue
from atlas import session

import pytest
import pandas as pd

import logging
import sys
import time
import os
import multiprocessing

# TODO:
#   Test maintainer task 
#   Test parametrization (parameter passing)
#   Test scheduler crashing

# Task funcs
def run_failing():
    raise RuntimeError("Task failed")

def run_succeeding():
    pass

def run_inacting():
    raise TaskInactionException()

def create_line_to_file():
    with open("work.txt", "a") as file:
        file.write("line created\n")

def run_with_param(int_5):
    assert int_5 == 5

def run_creating_child():

    proc = multiprocessing.Process(target=run_succeeding, daemon=True)
    proc.start()


@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_task_execution(tmpdir, execution):
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        # To be confident the scheduler won't lie to us
        # we test the task execution with a job that has
        # actual measurable impact outside atlas
        FuncTask(create_line_to_file, name="add line to file", start_cond=AlwaysTrue(), execution=execution),
        scheduler = Scheduler(
            shut_condition=TaskStarted(task="add line to file") >= 3,
        )

        scheduler()

        with open("work.txt", "r") as file:
            assert 3 == len(list(file))

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
@pytest.mark.parametrize(
    "task_func,run_count,fail_count,success_count",
    [
        pytest.param(
            run_succeeding, 
            3, 0, 3,
            id="Succeeding task"),

        pytest.param(
            run_failing, 
            3, 3, 0,
            id="Failing task"),
        pytest.param(
            run_inacting, 
            3, 0, 0,
            id="Inacting task"),
    ],
)
def test_task_log(tmpdir, execution, task_func, run_count, fail_count, success_count):
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = FuncTask(task_func, name="task", start_cond=AlwaysTrue(), execution=execution)

        scheduler = Scheduler(
            shut_condition=TaskStarted(task="task") >= run_count
        )
        scheduler()

        history = pd.DataFrame(task.get_history())
        assert run_count == (history["action"] == "run").sum()
        assert success_count == (history["action"] == "success").sum()
        assert fail_count == (history["action"] == "fail").sum()


@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_task_force_run(tmpdir, execution):
    with tmpdir.as_cwd() as old_dir:
        session.reset()

        task = FuncTask(
            run_succeeding, 
            start_cond=AlwaysFalse(), 
            name="task",
            execution=execution
        )
        task.force_run = True

        scheduler = Scheduler(
            shut_condition=~SchedulerStarted(period=TimeDelta("1 second"))
        )
        scheduler()

        history = pd.DataFrame(task.get_history())
        assert 1 == (history["action"] == "run").sum()

        # The force_run should have reseted as it should have run once
        assert not task.force_run


@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_task_disabled(tmpdir, execution):
    with tmpdir.as_cwd() as old_dir:
        session.reset()

        task = FuncTask(
            run_succeeding, 
            start_cond=AlwaysFalse(), 
            name="task",
            execution=execution
        )
        task.disabled = True

        scheduler = Scheduler(
            shut_condition=~SchedulerStarted(period=TimeDelta("1 second"))
        )
        scheduler()

        history = task.get_history()
        assert 0 == sum([record for record in history if record["action"] == "run"])

        assert task.disabled


@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_task_force_disabled(tmpdir, execution):
    # NOTE: force_run overrides disabled
    # as it is more practical to keep 
    # a task disabled and force it running
    # manually than prevent force run with
    # disabling
    with tmpdir.as_cwd() as old_dir:
        session.reset()

        task = FuncTask(
            run_succeeding, 
            start_cond=AlwaysFalse(), 
            name="task",
            execution=execution
        )
        task.disabled = True
        task.force_run = True

        scheduler = Scheduler(
            shut_condition=~SchedulerStarted(period=TimeDelta("1 second"))
        )
        scheduler()

        history = pd.DataFrame(task.get_history())
        assert 1 == (history["action"] == "run").sum()

        assert task.disabled
        assert not task.force_run # This should be reseted

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_priority(tmpdir, execution):
    with tmpdir.as_cwd() as old_dir:
        session.reset()

        task_1 = FuncTask(run_succeeding, priority=1, name="first", start_cond=AlwaysTrue(), execution=execution)
        task_2 = FuncTask(run_failing, priority=10, name="last", start_cond=AlwaysTrue(), execution=execution)
        task_3 = FuncTask(run_failing, priority=5, name="second", start_cond=AlwaysTrue(), execution=execution)
        scheduler = Scheduler(
            shut_condition=(TaskStarted(task="last") >= 1) | ~SchedulerStarted(period=TimeDelta("2 seconds"))
        )

        scheduler()
        assert scheduler.n_cycles == 1

        history = pd.DataFrame(session.get_task_log())
        history = history.set_index("action")

        task_1_start = history[(history["task_name"] == "first")].loc["run", "asctime"]
        task_3_start = history[(history["task_name"] == "second")].loc["run", "asctime"]
        task_2_start = history[(history["task_name"] == "last")].loc["run", "asctime"]
        
        assert task_1_start < task_3_start < task_2_start

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_pass_params_as_global(tmpdir, execution):
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = FuncTask(run_with_param, name="parametrized", start_cond=AlwaysTrue(), execution=execution)
        scheduler = Scheduler(
            shut_condition=(TaskStarted(task="parametrized") >= 1) | ~SchedulerStarted(period=TimeDelta("2 seconds"))
        )

        # Passing global parameters
        session.parameters["int_5"] = 5
        session.parameters["extra_param"] = "something"

        scheduler()

        history = pd.DataFrame(task.get_history())
        assert 1 == (history["action"] == "run").sum()
        assert 1 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_pass_params_as_local(tmpdir, execution):
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = FuncTask(
            run_with_param, 
            name="parametrized", 
            parameters={"int_5": 5, "extra_param": "something"},
            start_cond=AlwaysTrue(),
            execution=execution
        )
        scheduler = Scheduler(
            shut_condition=(TaskStarted(task="parametrized") >= 1) | ~SchedulerStarted(period=TimeDelta("2 seconds"))
        )

        scheduler()

        history = pd.DataFrame(task.get_history())
        assert 1 == (history["action"] == "run").sum()
        assert 1 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_pass_params_as_local_and_global(tmpdir, execution):
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = FuncTask(
            run_with_param, 
            name="parametrized", 
            parameters={"int_5": 5},
            start_cond=AlwaysTrue(),
            execution=execution
        )
        scheduler = Scheduler(
            shut_condition=(TaskStarted(task="parametrized") >= 1) | ~SchedulerStarted(period=TimeDelta("2 seconds"))
        )

        # Additional parameters
        session.parameters["extra_param"] = "something"

        scheduler()

        history = pd.DataFrame(task.get_history())
        assert 1 == (history["action"] == "run").sum()
        assert 1 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()


# Maintainer


# Only needed for testing start up and shutdown
def create_line_to_startup_file():
    with open("start.txt", "w") as file:
        file.write("line created\n")

def create_line_to_shutdown():
    with open("shut.txt", "w") as file:
        file.write("line created\n")

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_startup_shutdown(tmpdir, execution):
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        
        FuncTask(create_line_to_startup_file, name="startup", on_startup=True, execution=execution)
        FuncTask(create_line_to_shutdown, name="shutdown", on_shutdown=True, execution=execution)

        scheduler = Scheduler(
            shut_condition=AlwaysTrue()
        )

        scheduler()
        if execution == "thread":
            # It may take a moment for the
            # thread to write to the file
            timeout = 5
            time_taken = 0
            while os.path.exists("shut.txt"):
                time.sleep(0.01)
                time_taken += 0.01
                if time_taken > timeout:
                    break
        
        assert os.path.exists("start.txt")
        assert os.path.exists("shut.txt")