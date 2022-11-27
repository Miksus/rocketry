import asyncio
import datetime
import logging
import time
import os
import re
import multiprocessing

import pytest

from redbird.logging import RepoHandler
from redbird.repos import MemoryRepo

from rocketry.log.log_record import TaskLogRecord
import rocketry
from rocketry import Session
from rocketry.core import Parameters
from rocketry.log.log_record import MinimalRecord
from rocketry.tasks import FuncTask
from rocketry.time import TimeDelta
from rocketry.exc import TaskInactionException, TaskTerminationException
from rocketry.conditions import SchedulerCycles, SchedulerStarted, TaskStarted, AlwaysFalse, AlwaysTrue
from rocketry.args import Private, TerminationFlag

from rocketry.conds import true, false

def run_failing():
    raise RuntimeError("Task failed")

def run_succeeding():
    pass

def run_inacting():
    raise TaskInactionException()

async def run_failing_async():
    raise RuntimeError("Task failed")

async def run_succeeding_async():
    pass

async def run_inacting_async():
    raise TaskInactionException()


def run_slow():
    time.sleep(5)

def run_slow_thread(flag=TerminationFlag()):
    t = 0
    while not flag.is_set() and t < 5:
        time.sleep(0.001)
        t += 0.001
    if flag.is_set():
        raise TaskTerminationException()

async def run_slow_async():
    await asyncio.sleep(5)


def create_line_to_file():
    with open("work.txt", "a", encoding="utf-8") as file:
        file.write("line created\n")

async def create_line_to_file_async():
    with open("work.txt", "a", encoding="utf-8") as file:
        file.write("line created\n")

def run_with_param(int_5):
    assert int_5 == 5

def run_creating_child():

    proc = multiprocessing.Process(target=run_succeeding, daemon=True)
    proc.start()

def test_scheduler_shut_cond(session):
    assert not session.scheduler.check_shut_cond(None)

    assert session.scheduler.check_shut_cond(true)
    assert not session.scheduler.check_shut_cond(~true)
    assert session.scheduler.check_shut_cond(true & true)
    assert not session.scheduler.check_shut_cond(false)

@pytest.mark.parametrize("execution", ["main", "async", "thread", "process"])
@pytest.mark.parametrize("func", [pytest.param(create_line_to_file, id="sync"), pytest.param(create_line_to_file_async, id="async")])
def test_task_execution(tmpdir, execution, func, session):
    with tmpdir.as_cwd():
        # To be confident the scheduler won't lie to us
        # we test the task execution with a job that has
        # actual measurable impact outside rocketry
        FuncTask(func, name="add line to file", start_cond=AlwaysTrue(), execution=execution, session=session)

        session.config.shut_cond = (TaskStarted(task="add line to file") >= 3) | ~SchedulerStarted(period=TimeDelta("5 second"))

        session.start()
        # Sometimes in CI the task may end up to be started only twice thus we tolerate slightly
        with open("work.txt", "r", encoding="utf-8") as file:
            assert 2 <= len(list(file))

@pytest.mark.parametrize("get_handler", [
    pytest.param(lambda: RepoHandler(repo=MemoryRepo(model=TaskLogRecord)), id="Memory with model"),
    pytest.param(lambda: RepoHandler(repo=MemoryRepo()), id="Memory with dict"),
])
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
def test_task_log(tmpdir, execution, task_func, run_count, fail_count, success_count, inact_count, get_handler):
    """Test the task logging thoroughly including the common
    logging schemes, execution (main, thread, process) and
    outcomes (fail, success, inaction).

    This task may take some time but should cover most of the
    issues with logging.
    """

    # Set session (and logging)
    session = Session(config={"debug": True, "silence_task_logging": False, "execution": "process"})
    rocketry.session = session
    session.set_as_default()

    task_logger = logging.getLogger(session.config.task_logger_basename)
    task_logger.handlers = [
        get_handler()
    ]

    task = FuncTask(task_func, name="mytask", start_cond=AlwaysTrue(), execution=execution, session=session)

    session.config.shut_cond = (TaskStarted(task="mytask") >= run_count) | ~SchedulerStarted(period=TimeDelta("10 second"))
    session.start()

    assert (TaskStarted(task="mytask") >= run_count).observe(session=session)

    # Test history
    history = list(task.logger.get_records())
    logger = task.logger
    assert run_count == logger.filter_by(action="run").count()
    assert success_count == logger.filter_by(action="success").count()
    assert fail_count == logger.filter_by(action="fail").count()
    assert inact_count == logger.filter_by(action="inaction").count()

    # Test relevant log items
    for record in history:
        is_tasl_log = isinstance(record, TaskLogRecord)
        if not isinstance(record, dict):
            record = record.dict()
        assert record["task_name"] == "mytask"
        assert isinstance(record["created"], float)
        assert isinstance(record["start"], datetime.datetime if is_tasl_log else float)
        if record["action"] != "run":
            assert isinstance(record["end"], datetime.datetime if is_tasl_log else float)
            assert isinstance(record["runtime"], datetime.timedelta if is_tasl_log else float)

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

@pytest.mark.parametrize("mode", ["use logs", "use cache"])
@pytest.mark.parametrize("func_type", ["sync", "async"])
@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_task_status(session, execution, func_type, mode):
    session.config.force_status_from_logs = mode == "use logs"

    task_success = FuncTask(
        run_succeeding if func_type == "sync" else run_succeeding_async,
        start_cond=TaskStarted(task="task success") < 3,
        name="task success",
        execution=execution,
        priority=0,
        session=session
    )
    task_fail = FuncTask(
        run_failing if func_type == "sync" else run_failing_async,
        start_cond=TaskStarted(task="task fail") < 3,
        name="task fail",
        execution=execution,
        priority=0,
        session=session
    )
    task_inact = FuncTask(
        run_inacting if func_type == "sync" else run_inacting_async,
        start_cond=TaskStarted(task="task inact") < 3,
        name="task inact",
        execution=execution,
        priority=100,
        session=session
    )
    task_not_run = FuncTask(
        run_inacting if func_type == "sync" else run_inacting_async,
        start_cond=false,
        name="task not run",
        execution=execution,
        priority=0,
        session=session
    )
    session.config.shut_cond = (
        (TaskStarted(task="task success") >= 3)
        & (TaskStarted(task="task fail") >= 3)
        & (TaskStarted(task="task inact") >= 3)
    ) | ~SchedulerStarted(period=TimeDelta("20 second"))
    session.start()

    # Test status
    assert task_success.last_run is not None
    assert task_success.last_success is not None
    assert task_success.last_fail is None

    assert task_fail.last_run is not None
    assert task_fail.last_fail is not None
    assert task_fail.last_success is None

    assert task_inact.last_run is not None

    assert task_not_run.last_run is None
    assert task_not_run.last_success is None
    assert task_not_run.last_fail is None

    assert task_success.status == "success"
    assert task_fail.status == "fail"
    assert task_inact.status == "inaction"
    assert task_not_run.status is None

    # Test logs
    assert 3 == task_success.logger.filter_by(action="run").count()
    assert 3 == task_fail.logger.filter_by(action="run").count()
    assert 3 == task_inact.logger.filter_by(action="run").count()
    assert 0 == task_not_run.logger.filter_by(action="run").count()

    assert 3 == task_success.logger.filter_by(action="success").count()
    assert 0 == task_fail.logger.filter_by(action="success").count()
    assert 0 == task_inact.logger.filter_by(action="suceess").count()

    assert 0 == task_success.logger.filter_by(action="fail").count()
    assert 3 == task_fail.logger.filter_by(action="fail").count()
    assert 0 == task_inact.logger.filter_by(action="fail").count()

    assert 0 == task_success.logger.filter_by(action="inaction").count()
    assert 0 == task_fail.logger.filter_by(action="inaction").count()
    assert 3 == task_inact.logger.filter_by(action="inaction").count()




@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_task_disabled(tmpdir, execution, session):
    with tmpdir.as_cwd():

        task = FuncTask(
            run_succeeding,
            start_cond=AlwaysFalse(),
            name="task",
            execution=execution,
            session=session
        )
        task.disabled = True

        session.config.shut_cond = SchedulerCycles() >= 5
        session.start()

        history = task.logger.get_records()
        assert 0 == sum(record for record in history if record["action"] == "run")

        assert task.disabled

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_priority(execution, session):
    session.config.max_process_count = 4
    task_1 = FuncTask(run_succeeding, name="1", priority=100, start_cond=AlwaysTrue(), execution=execution, session=session)
    task_3 = FuncTask(run_failing, name="3", priority=10, start_cond=AlwaysTrue(), execution=execution, session=session)
    task_2 = FuncTask(run_failing, name="2", priority=50, start_cond=AlwaysTrue(), execution=execution, session=session)
    task_4 = FuncTask(run_failing, name="4", start_cond=AlwaysTrue(), execution=execution, session=session)

    assert 0 == task_4.priority

    session.config.shut_cond = (SchedulerCycles() == 1) | ~SchedulerStarted(period=TimeDelta("20 seconds"))

    session.start()
    assert session.scheduler.n_cycles == 1

    task_1_start = list(task_1.logger.get_records())[0].created
    task_2_start = list(task_2.logger.get_records())[0].created
    task_3_start = list(task_3.logger.get_records())[0].created
    task_4_start = list(task_4.logger.get_records())[0].created

    assert task_1_start < task_2_start < task_3_start < task_4_start

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_pass_params_as_global(execution, session):
    # thread-Parameters has been observed to fail rarely

    task = FuncTask(run_with_param, name="parametrized", start_cond=AlwaysTrue(), execution=execution, session=session)

    session.config.shut_cond = (TaskStarted(task="parametrized") >= 1) | ~SchedulerStarted(period=TimeDelta("20 seconds"))

    # Passing global parameters
    session.parameters["int_5"] = 5
    session.parameters["extra_param"] = "something"

    session.scheduler()

    logger = task.logger
    assert 1 == logger.filter_by(action="run").count()
    assert 1 == logger.filter_by(action="success").count()
    assert 0 == logger.filter_by(action="fail").count()

@pytest.mark.parametrize("parameters", [
    pytest.param({"int_5": 5}, id="dict"),
    pytest.param(Parameters(int_5=5), id="Parameters"),
    pytest.param(Parameters(int_5=Private(5)), id="Parameter with secret"),
])
@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_pass_params_as_local(execution, parameters, session):

    task = FuncTask(
        run_with_param,
        name="parametrized",
        parameters=parameters,
        start_cond=AlwaysTrue(),
        execution=execution,
        session=session
    )
    session.config.shut_cond = (TaskStarted(task="parametrized") >= 1) | ~SchedulerStarted(period=TimeDelta("20 seconds"))

    session.start()

    logger = task.logger
    assert 1 == logger.filter_by(action="run").count()
    assert 1 == logger.filter_by(action="success").count()
    assert 0 == logger.filter_by(action="fail").count()

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_pass_params_as_local_and_global(execution, session):

    task = FuncTask(
        run_with_param,
        name="parametrized",
        parameters={"int_5": 5},
        start_cond=AlwaysTrue(),
        execution=execution,
        session=session
    )

    session.config.shut_cond = (TaskStarted(task="parametrized") >= 1) | ~SchedulerStarted(period=TimeDelta("20 seconds"))

    # Additional parameters
    session.parameters["extra_param"] = "something"

    session.start()

    logger = task.logger
    assert 1 == logger.filter_by(action="run").count()
    assert 1 == logger.filter_by(action="success").count()
    assert 0 == logger.filter_by(action="fail").count()


# Only needed for testing start up and shutdown
def create_line_to_startup_file():
    with open("start.txt", "w", encoding="utf-8") as file:
        file.write("line created\n")

def create_line_to_shutdown():
    with open("shut.txt", "w", encoding="utf-8") as file:
        file.write("line created\n")

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_startup_shutdown(tmpdir, execution, session):
    with tmpdir.as_cwd():

        FuncTask(create_line_to_startup_file, name="startup", on_startup=True, execution=execution, session=session)
        FuncTask(create_line_to_shutdown, name="shutdown", on_shutdown=True, execution=execution, session=session)

        session.config.shut_cond = AlwaysTrue()

        session.start()
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

        assert list(session.get_task_log())

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_logging_repo(tmpdir, execution):
    session = Session(config={'execution': 'async'})
    session.set_as_default()
    session.config.max_process_count = 4

    handler = RepoHandler(repo=MemoryRepo(model=MinimalRecord))

    logger = logging.getLogger("rocketry.task")
    logger.handlers = []
    logger.addHandler(handler)


    with tmpdir.as_cwd():

        task_1 = FuncTask(run_succeeding, name="1", priority=100, start_cond=AlwaysTrue(), execution=execution, session=session)
        task_3 = FuncTask(run_failing, name="3", priority=10, start_cond=AlwaysTrue(), execution=execution, session=session)
        task_2 = FuncTask(run_failing, name="2", priority=50, start_cond=AlwaysTrue(), execution=execution, session=session)
        task_4 = FuncTask(run_failing, name="4", start_cond=AlwaysTrue(), execution=execution, session=session)

        assert 0 == task_4.priority

        session.config.shut_cond = (SchedulerCycles() == 1) | ~SchedulerStarted(period=TimeDelta("20 seconds"))
        session.start()
        assert session.scheduler.n_cycles == 1

        task_1_start = list(task_1.logger.get_records())[0].created
        task_2_start = list(task_2.logger.get_records())[0].created
        task_3_start = list(task_3.logger.get_records())[0].created
        task_4_start = list(task_4.logger.get_records())[0].created

        assert task_1_start < task_2_start < task_3_start < task_4_start

@pytest.mark.parametrize("execution", ["async", "thread", "process"])
def test_instant_shutdown(execution, session):
    assert not session.config.instant_shutdown
    session.config.instant_shutdown = True

    func = {"async": run_slow_async, "thread": run_slow_thread, "process": run_slow}[execution]

    task = FuncTask(func, execution=execution, start_cond=true, end_cond=SchedulerCycles() == 2, session=session)

    session.config.shut_cond = SchedulerCycles() == 2

    session.start()

    assert 1 == task.logger.filter_by(action="run").count()
    assert 2 == task.logger.filter_by().count()

    assert 0 == task.logger.filter_by(action="fail").count()
    assert 0 == task.logger.filter_by(action="success").count()
    assert 1 == task.logger.filter_by(action="terminate").count()

def test_cycle_sleep_none(session):
    assert not session.config.instant_shutdown
    session.config.instant_shutdown = True
    session.config.cycle_sleep = None

    order = []

    async def run_async():
        order.append("async start")
        await asyncio.sleep(0)
        order.append("async end")

    def run_shutdown():
        order.append("shutdown task")

    FuncTask(run_async, execution="async", start_cond=true, session=session)
    FuncTask(run_shutdown, execution="main", start_cond=true, session=session)

    session.config.shut_cond = SchedulerCycles() == 1

    session.start()

    assert order == [
        "async start",
        "shutdown task",
        "async end"
    ]
