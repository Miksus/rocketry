
import datetime
import time
import os, re
import multiprocessing

import pytest
import pandas as pd

import redengine
from redengine import Session
from redengine.core import Scheduler, Parameters
from redengine.tasks import FuncTask
from redengine.time import TimeDelta
from redengine.core.exceptions import TaskInactionException
from redengine.conditions import SchedulerCycles, SchedulerStarted, TaskStarted, AlwaysFalse, AlwaysTrue
from redengine.arguments import Private

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
def test_task_execution(tmpdir, execution, session):
    with tmpdir.as_cwd() as old_dir:
        # To be confident the scheduler won't lie to us
        # we test the task execution with a job that has
        # actual measurable impact outside redengine
        FuncTask(create_line_to_file, name="add line to file", start_cond=AlwaysTrue(), execution=execution),
        scheduler = Scheduler(
            shut_cond=(TaskStarted(task="add line to file") >= 3) | ~SchedulerStarted(period=TimeDelta("5 second")),
        )

        scheduler()

        with open("work.txt", "r") as file:
            assert 3 == len(list(file))

@pytest.mark.parametrize("logging_scheme", ["memory_logging", "csv_logging"])
@pytest.mark.parametrize("execution", ["main", "thread", "process"])
@pytest.mark.parametrize(
    "task_func,run_count,fail_count,success_count,inact_count",
    [
        pytest.param(
            run_succeeding, 
            3, 0, 3, 0,
            id="Succeeding task"),

        pytest.param(
            run_failing, 
            3, 3, 0, 0,
            id="Failing task"),
        pytest.param(
            run_inacting, 
            3, 0, 0, 3,
            id="Inacting task"),
    ],
)
def test_task_log(tmpdir, execution, task_func, run_count, fail_count, success_count, inact_count, logging_scheme):
    """Test the task logging thoroughly including the common
    logging schemes, execution (main, thread, process) and 
    outcomes (fail, success, inaction).

    This task may take some time but should cover most of the
    issues with logging.
    """

    with tmpdir.as_cwd() as old_dir:

        # Set session (and logging)
        session = Session(scheme=logging_scheme, config={"debug": True})
        redengine.session = session
        session.set_as_default()

        task = FuncTask(task_func, name="mytask", start_cond=AlwaysTrue(), execution=execution)

        scheduler = Scheduler(
            shut_cond=TaskStarted(task="mytask") >= run_count
        )
        scheduler()

        # Test history
        history = list(task.logger.get_records())
        assert run_count == len([rec for rec in history if rec["action"] == "run"])
        assert success_count == len([rec for rec in history if rec["action"] == "success"])
        assert fail_count == len([rec for rec in history if rec["action"] == "fail"])
        assert inact_count == len([rec for rec in history if rec["action"] == "inaction"])

        # Test relevant log items
        for record in history:
            assert record["task_name"] == "mytask"
            assert isinstance(record["timestamp"], datetime.datetime)
            assert isinstance(record["start"], datetime.datetime)
            if record["action"] != "run":
                assert isinstance(record["end"], datetime.datetime)
                assert isinstance(record["runtime"], datetime.timedelta)

            # Test traceback
            if record["action"] == "fail":
                assert re.match(
                    r'Traceback \(most recent call last\):\n  File ".+", line [0-9]+, in [\s\S]+, in run_failing\n    raise RuntimeError\("Task failed"\)\nRuntimeError: Task failed', 
                    record["exc_text"]
                )

        # Test some other relevant APIs
        assert history == list(task.logger.get_records())
        assert history[-1] == task.logger.get_latest()
        assert history == list(session.get_task_log())

        assert run_count == len(list(task.logger.get_records(action="run")))
        assert success_count == len(list(task.logger.get_records(action="success")))
        assert fail_count == len(list(task.logger.get_records(action="fail")))
        assert inact_count == len(list(task.logger.get_records(action="inaction")))

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_task_force_run(tmpdir, execution, session):
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            run_succeeding, 
            start_cond=AlwaysFalse(), 
            name="task",
            execution=execution
        )
        task.force_run = True

        scheduler = Scheduler(
            shut_cond=~SchedulerStarted(period=TimeDelta("1 second"))
        )
        scheduler()

        history = pd.DataFrame(task.logger.get_records())
        assert 1 == (history["action"] == "run").sum()

        # The force_run should have reseted as it should have run once
        assert not task.force_run


@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_task_disabled(tmpdir, execution, session):
    with tmpdir.as_cwd() as old_dir:

        task = FuncTask(
            run_succeeding, 
            start_cond=AlwaysFalse(), 
            name="task",
            execution=execution
        )
        task.disabled = True

        scheduler = Scheduler(
            shut_cond=~SchedulerStarted(period=TimeDelta("1 second"))
        )
        scheduler()

        history = task.logger.get_records()
        assert 0 == sum([record for record in history if record["action"] == "run"])

        assert task.disabled


@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_task_force_disabled(tmpdir, execution, session):
    # NOTE: force_run overrides disabled
    # as it is more practical to keep 
    # a task disabled and force it running
    # manually than prevent force run with
    # disabling
    with tmpdir.as_cwd() as old_dir:

        task = FuncTask(
            run_succeeding, 
            start_cond=AlwaysFalse(), 
            name="task",
            execution=execution
        )
        task.disabled = True
        task.force_run = True

        scheduler = Scheduler(
            shut_cond=~SchedulerStarted(period=TimeDelta("1 second"))
        )
        scheduler()

        history = pd.DataFrame(task.logger.get_records())
        assert 1 == (history["action"] == "run").sum()

        assert task.disabled
        assert not task.force_run # This should be reseted

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_priority(tmpdir, execution, session):
    with tmpdir.as_cwd() as old_dir:

        task_1 = FuncTask(run_succeeding, name="1", priority=100, start_cond=AlwaysTrue(), execution=execution)
        task_3 = FuncTask(run_failing, name="3", priority=10, start_cond=AlwaysTrue(), execution=execution)
        task_2 = FuncTask(run_failing, name="2", priority=50, start_cond=AlwaysTrue(), execution=execution)
        task_4 = FuncTask(run_failing, name="4", start_cond=AlwaysTrue(), execution=execution)

        assert 0 == task_4.priority

        scheduler = Scheduler(
            shut_cond=(SchedulerCycles() == 1) | ~SchedulerStarted(period=TimeDelta("2 seconds"))
        )

        scheduler()
        assert scheduler.n_cycles == 1 

        task_1_start = list(task_1.logger.get_records())[0]["timestamp"]
        task_2_start = list(task_2.logger.get_records())[0]["timestamp"]
        task_3_start = list(task_3.logger.get_records())[0]["timestamp"]
        task_4_start = list(task_4.logger.get_records())[0]["timestamp"]
        
        assert task_1_start < task_2_start < task_3_start < task_4_start

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_pass_params_as_global(tmpdir, execution, session):
    # thread-Parameters has been observed to fail rarely
    with tmpdir.as_cwd() as old_dir:

        task = FuncTask(run_with_param, name="parametrized", start_cond=AlwaysTrue(), execution=execution)
        scheduler = Scheduler(
            shut_cond=(TaskStarted(task="parametrized") >= 1) | ~SchedulerStarted(period=TimeDelta("2 seconds"))
        )

        # Passing global parameters
        session.parameters["int_5"] = 5
        session.parameters["extra_param"] = "something"

        scheduler()

        history = pd.DataFrame(task.logger.get_records())
        assert 1 == (history["action"] == "run").sum()
        assert 1 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()

@pytest.mark.parametrize("parameters", [
    pytest.param({"int_5": 5}, id="dict"), 
    pytest.param(Parameters(int_5=5), id="Parameters"),
    pytest.param(Parameters(int_5=Private(5)), id="Parameter with secret"),
])
@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_pass_params_as_local(tmpdir, execution, parameters, session):
    with tmpdir.as_cwd() as old_dir:

        task = FuncTask(
            run_with_param, 
            name="parametrized", 
            parameters=parameters,
            start_cond=AlwaysTrue(),
            execution=execution
        )
        scheduler = Scheduler(
            shut_cond=(TaskStarted(task="parametrized") >= 1) | ~SchedulerStarted(period=TimeDelta("2 seconds"))
        )

        scheduler()

        history = pd.DataFrame(task.logger.get_records())
        assert 1 == (history["action"] == "run").sum()
        assert 1 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_pass_params_as_local_and_global(tmpdir, execution, session):
    with tmpdir.as_cwd() as old_dir:

        task = FuncTask(
            run_with_param, 
            name="parametrized", 
            parameters={"int_5": 5},
            start_cond=AlwaysTrue(),
            execution=execution
        )
        scheduler = Scheduler(
            shut_cond=(TaskStarted(task="parametrized") >= 1) | ~SchedulerStarted(period=TimeDelta("2 seconds"))
        )

        # Additional parameters
        session.parameters["extra_param"] = "something"

        scheduler()

        history = pd.DataFrame(task.logger.get_records())
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
def test_startup_shutdown(tmpdir, execution, session):
    with tmpdir.as_cwd() as old_dir:
        
        FuncTask(create_line_to_startup_file, name="startup", on_startup=True, execution=execution)
        FuncTask(create_line_to_shutdown, name="shutdown", on_shutdown=True, execution=execution)

        scheduler = Scheduler(
            shut_cond=AlwaysTrue()
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

        assert list(session.get_task_log()) != []
        assert list(session.get_scheduler_log()) != []