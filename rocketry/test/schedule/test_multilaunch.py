import asyncio
import datetime
import json
import time

import pytest
from rocketry.args import FuncArg
from rocketry.conds import scheduler_cycles, false, true

from rocketry.tasks import FuncTask
from rocketry.exc import TaskTerminationException
from rocketry.conditions import SchedulerCycles, TaskStarted
from rocketry.args import TerminationFlag
from rocketry.log import RunRecord
from rocketry.tasks.run_id import increment, uuid


def run_success_instant():
    ...

def run_slow_fail():
    time.sleep(5)
    raise

def run_slow_success():
    time.sleep(5)

def run_slow_threaded_fail(_thread_terminate_):
    time.sleep(0.2)
    if _thread_terminate_.is_set():
        raise TaskTerminationException
    raise

async def run_slow_async_fail():
    await asyncio.sleep(0.2)
    raise

async def run_success():
    await asyncio.sleep(0.1)

async def run_fail():
    await asyncio.sleep(0.1)
    raise RuntimeError("Oops")

def get_slow_func(execution):
    return {
        "async": run_slow_async_fail,
        "process": run_slow_fail,
        # Thread tasks are terminated inside the task (the task should respect _thread_terminate_)
        "thread": run_slow_threaded_fail,
    }[execution]

@pytest.mark.parametrize("how", ["config", "task"])
@pytest.mark.parametrize("execution", ["async", "thread", "process"])
def test_multilaunch_terminate(execution, how, session):
    # Start 5 time
    session.config.instant_shutdown = True
    session.config.max_process_count = 3

    if how == "config":
        session.config.multilaunch = True
    else:
        session.config.multilaunch = False

    func_run_slow = get_slow_func(execution)
    task = FuncTask(
        func_run_slow, name="slow task",
        start_cond=TaskStarted() <= 3,
        multilaunch=True if how == "task" else None,
        execution=execution, session=session
    )
    session.config.shut_cond = (TaskStarted(task="slow task") >= 3)
    session.start()

    logger = task.logger
    logs = [{"action": rec.action} for rec in logger.filter_by()]
    assert logs == [
        {"action": "run"},
        {"action": "run"},
        {"action": "run"},
        {"action": "terminate"},
        {"action": "terminate"},
        {"action": "terminate"},
    ]

@pytest.mark.parametrize("execution", ["async", "thread", "process"])
def test_multilaunch_terminate_end_cond(execution, session):
    session.config.func_run_id = increment
    session.get_repo().model = RunRecord
    # Start 5 time
    session.config.max_process_count = 3

    func_run_slow = get_slow_func(execution)
    task = FuncTask(func_run_slow, name="slow task", start_cond=TaskStarted() <= 3, end_cond=TaskStarted() == 3, multilaunch=True, execution=execution, session=session)
    session.config.shut_cond = (TaskStarted(task="slow task") >= 3)
    session.start()

    logger = task.logger
    logs = [{"task_name": rec.task_name, "action": rec.action, "run_id": rec.run_id} for rec in logger.filter_by()]
    assert logs == [
        {"task_name": "slow task", "action": "run", "run_id": "1"},
        {"task_name": "slow task", "action": "run", "run_id": "2"},
        {"task_name": "slow task", "action": "run", "run_id": "3"},
        {"task_name": "slow task", "action": "terminate", "run_id": "1"},
        {"task_name": "slow task", "action": "terminate", "run_id": "2"},
        {"task_name": "slow task", "action": "terminate", "run_id": "3"},
    ]

@pytest.mark.parametrize("status", ["success", "fail"])
@pytest.mark.parametrize("execution", ["async", "thread", "process"])
def test_multilaunch(execution, status, session):
    session.config.func_run_id = increment
    session.get_repo().model = RunRecord
    if execution == "process":
        pytest.skip(reason="Process too unreliable to test")
    # Start 5 time
    session.config.max_process_count = 3

    task = FuncTask(
        run_success if status == "success" else run_fail,
        name="task",
        start_cond=TaskStarted() <= 5,
        multilaunch=True,
        execution=execution, session=session,
    )
    session.config.shut_cond = (TaskStarted(task="task") >= 3)
    session.start()

    logger = task.logger
    logs = [{"task_name": rec.task_name, "action": rec.action, "run_id": rec.run_id} for rec in logger.filter_by()]
    if execution == 'async':
        assert logs == [
            {"task_name": "task", "action": "run", "run_id": "1"},
            {"task_name": "task", "action": "run", "run_id": "2"},
            {"task_name": "task", "action": "run", "run_id": "3"},
            {"task_name": "task", "action": status, "run_id": "1"},
            {"task_name": "task", "action": status, "run_id": "2"},
            {"task_name": "task", "action": status, "run_id": "3"},
        ]
    else:
        # In thread the runs can finish in different order
        assert logs[:3] == [
            {"task_name": "task", "action": "run", "run_id": "1"},
            {"task_name": "task", "action": "run", "run_id": "2"},
            {"task_name": "task", "action": "run", "run_id": "3"},
        ]
        assert {log['run_id'] for log in logs[3:]} == {"1", "2", "3"}
        for log in logs[3:]:
            log.pop("run_id")
        assert logs[3:] == [
            {"task_name": "task", "action": status},
            {"task_name": "task", "action": status},
            {"task_name": "task", "action": status},
        ]

def test_multilaunch_terminate_after_success(session):
    # Issue #144
    session.config.func_run_id = increment
    session.get_repo().model = RunRecord
    session.config.max_process_count = 3

    task = FuncTask(
        run_success_instant,
        name="task",
        start_cond=true,
        multilaunch=True,
        execution="process", session=session,
    )
    session.config.shut_cond = TaskStarted(task=task)
    session.start()
    logger = task.logger
    logs = [{"task_name": rec.task_name, "action": rec.action, "run_id": rec.run_id} for rec in logger.filter_by()]
    assert logs == [
        {"task_name": "task", "action": "run", "run_id": "1"},
        {"task_name": "task", "action": "success", "run_id": "1"},
    ]

    task.start_cond = false
    session.config.timeout = 0.0
    session.config.shut_cond = scheduler_cycles(5)
    session.start()

    logger = task.logger
    logs = [{"task_name": rec.task_name, "action": rec.action, "run_id": rec.run_id} for rec in logger.filter_by()]
    assert logs == [
        {"task_name": "task", "action": "run", "run_id": "1"},
        {"task_name": "task", "action": "success", "run_id": "1"},
    ]
    assert task._run_stack == []

def test_limited_processes(session):

    def run_thread(flag=TerminationFlag()):
        while not flag.is_set():
            ...

    async def run_async():
        while True:
            await asyncio.sleep(0)

    def do_post_check():
        sched = session.scheduler

        assert task_threaded.is_alive()
        assert task_threaded.is_running
        assert task_async.is_alive()
        assert task_async.is_running

        assert task1.is_alive()
        assert task2.is_alive()

        assert task1.is_running
        assert task2.is_running


        assert task1.n_alive == 3
        assert task2.n_alive == 1

        assert sched.n_alive == 7 # 3 processes, 1 thread, 1 async and this
        assert not sched.has_free_processors()

    task_threaded = FuncTask(run_thread, name="threaded", priority=4, start_cond=true, execution="thread", permanent=True, session=session)
    task_async = FuncTask(run_async, name="async", priority=4, start_cond=true, execution="async", permanent=True, session=session)
    post_check = FuncTask(do_post_check, name="post_check", on_shutdown=True, execution="main", session=session)

    task1 = FuncTask(run_slow_success, name="task_1", priority=3, start_cond=true, execution="process", session=session, multilaunch=True)
    task2 = FuncTask(run_slow_success, name="task_3", priority=1, start_cond=true, execution="process", session=session)

    session.config.max_process_count = 4
    session.config.instant_shutdown = True
    session.config.shut_cond = SchedulerCycles() >= 3

    session.start()

    outcome = post_check.logger.filter_by().all()[-1]
    assert outcome.action == "success", outcome.exc_text

@pytest.mark.parametrize("func", [increment, uuid])
@pytest.mark.parametrize("where", ["task", "session"])
def test_set_run_id(where, func, session):
    if where == "session":
        session.config.func_run_id = func
    session.get_repo().model = RunRecord

    async def run_task(report_date):
        assert isinstance(report_date, datetime.datetime)
        await asyncio.sleep(0.2)

    # Start 5 time
    session.config.max_process_count = 3

    kwds = dict(
        func=run_task,
        name="task",
        start_cond=TaskStarted() <= 5,
        multilaunch=True,
        execution="async",
        session=session,
        parameters={"report_date": datetime.datetime(2022, 1, 3)},
    )
    if where == 'task':
        kwds['func_run_id'] = func
    task = FuncTask(
        **kwds
    )
    task.run(report_date=datetime.datetime(2022, 1, 1))
    task.run(report_date=datetime.datetime(2022, 1, 2))

    session.config.shut_cond = (TaskStarted(task="task") >= 3)
    session.start()

    logger = task.logger
    logs = [{"task_name": rec.task_name, "action": rec.action} for rec in logger.filter_by()]
    assert logs == [
        {"task_name": "task", "action": "run"},
        {"task_name": "task", "action": "run"},
        {"task_name": "task", "action": "run"},
        {"task_name": "task", "action": "success"},
        {"task_name": "task", "action": "success"},
        {"task_name": "task", "action": "success"},
    ]
    # Check they are unique
    ids = [rec.run_id for rec in logger.filter_by()]
    assert len(set(ids)) == 3

def test_set_run_id_custom(session):
    session.get_repo().model = RunRecord

    def generate_run_id(task, params):
        return json.dumps(dict(params), default=str)

    async def run_task(report_date):
        assert isinstance(report_date, datetime.date)
        await asyncio.sleep(0.2)

    # Start 5 time
    session.config.max_process_count = 3

    task = FuncTask(
        func=run_task,
        name="task",
        start_cond=TaskStarted() <= 5,
        multilaunch=True,
        execution="async",
        session=session,
        parameters={"report_date": FuncArg(lambda: datetime.date(2022, 1, 3))},
        func_run_id=generate_run_id
    )
    task.run(report_date=datetime.date(2022, 1, 1))
    task.run(report_date=datetime.date(2022, 1, 2))

    session.config.shut_cond = (TaskStarted(task="task") >= 3)
    session.start()

    logger = task.logger
    logs = [{"task_name": rec.task_name, "action": rec.action, "run_id": rec.run_id} for rec in logger.filter_by()]
    assert logs == [
        {"task_name": "task", "action": "run", "run_id": '{"report_date": "2022-01-01"}'},
        {"task_name": "task", "action": "run", "run_id": '{"report_date": "2022-01-02"}'},
        {"task_name": "task", "action": "run", "run_id": '{"report_date": "2022-01-03"}'},
        {"task_name": "task", "action": "success", "run_id": '{"report_date": "2022-01-01"}'},
        {"task_name": "task", "action": "success", "run_id": '{"report_date": "2022-01-02"}'},
        {"task_name": "task", "action": "success", "run_id": '{"report_date": "2022-01-03"}'},
    ]
