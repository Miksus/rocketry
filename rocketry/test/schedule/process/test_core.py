import asyncio
import multiprocessing
import time
import logging

from redbird.repos import MemoryRepo
from redbird.logging import RepoHandler

from rocketry.args.builtin import TerminationFlag
from rocketry.conditions.scheduler import SchedulerCycles

from rocketry.log import LogRecord
from rocketry.tasks import FuncTask
from rocketry.time import TimeDelta
from rocketry.conds import true
from rocketry.conditions import SchedulerStarted, TaskStarted, AlwaysTrue

def run_succeeding():
    pass

def run_succeeding_slow():
    time.sleep(20)

def run_creating_child():

    proc = multiprocessing.Process(target=run_succeeding, daemon=True)
    proc.start()

def test_creating_child(session):

    FuncTask(run_creating_child, name="task_1", start_cond=AlwaysTrue(), session=session)

    session.config.tasks_as_daemon = False
    session.config.shut_cond = (TaskStarted(task="task_1") >= 1) | ~SchedulerStarted(period=TimeDelta("1 second"))

    session.start()

    logger = session["task_1"].logger
    assert 1 == logger.filter_by(action="run").count()
    assert 1 == logger.filter_by(action="success").count()
    assert 0 == logger.filter_by(action="fail").count()

def test_limited_processes(session):
    task_logger = logging.getLogger(session.config.task_logger_basename)
    task_logger.handlers = [
        RepoHandler(repo=MemoryRepo(model=LogRecord)),
    ]

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
        assert not task3.is_alive()

        assert task1.is_running
        assert task2.is_running
        assert not task3.is_running

        assert sched.n_alive == 5 # 2 processes, 1 thread, 1 async and this
        assert not sched.has_free_processors()

    task_threaded = FuncTask(run_thread, name="threaded", priority=4, start_cond=true, execution="thread", permanent=True, session=session)
    task_async = FuncTask(run_async, name="async", priority=4, start_cond=true, execution="async", permanent=True, session=session)
    post_check = FuncTask(do_post_check, name="post_check", on_shutdown=True, execution="main", session=session)

    task1 = FuncTask(run_succeeding_slow, name="task_1", priority=3, start_cond=true, execution="process", session=session)
    task2 = FuncTask(run_succeeding_slow, name="task_2", priority=2, start_cond=true, execution="process", session=session)
    task3 = FuncTask(run_succeeding_slow, name="task_3", priority=1, start_cond=true, execution="process", session=session)

    session.config.max_process_count = 2
    session.config.instant_shutdown = True
    session.config.shut_cond = SchedulerCycles() >= 3

    session.start()

    outcome = post_check.logger.filter_by().all()[-1]
    assert outcome.action == "success", outcome.exc_text
