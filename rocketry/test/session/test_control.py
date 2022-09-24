
import asyncio
import time
import pytest

from rocketry.args import Session
import rocketry
from rocketry.args.builtin import TerminationFlag
from rocketry.conditions.scheduler import SchedulerStarted
from rocketry.conditions import TaskStarted
from rocketry.core.time.base import TimeDelta
from rocketry.tasks import FuncTask
from rocketry.conds import true
from rocketry.exc import TaskTerminationException


@pytest.mark.parametrize("execution", ["main", "thread"])
def test_shutdown(execution, session):
    timeline = []

    def on_startup():
        timeline.append("startup")

    def call_shutdown(session:rocketry.Session=Session()):
        session.shut_down()
        timeline.append("shutdown-called")

    def on_shutdown():
        timeline.append("shutdown")


    FuncTask(on_startup, name="startup", on_startup=True, start_cond=true, execution=execution, session=session)
    FuncTask(call_shutdown, name="call-shutdown", start_cond=true, execution=execution, session=session)
    FuncTask(on_shutdown, name="shutdown", on_shutdown=True, start_cond=true, execution=execution, session=session)


    session.config.shut_cond = TaskStarted(task="call-shutdown") >= 3

    session.start()
    assert timeline == ['startup', 'shutdown-called', 'shutdown']

@pytest.mark.parametrize("doublecall", [False, True])
@pytest.mark.parametrize("execution", ["async", "thread"])
def test_shutdown_force(execution, session, doublecall):
    timeline = []

    def on_startup():
        timeline.append("startup")

    async def slow_task_async():
        await asyncio.sleep(2)

    def slow_task_thread(flag=TerminationFlag()):
        while not flag.is_set():
            time.sleep(0.001)
        if flag.is_set():
            raise TaskTerminationException()

    def call_shutdown(session:rocketry.Session=Session()):
        if doublecall:
            session.shut_down()
            session.shut_down()
        else:
            session.shut_down(force=True)
        timeline.append("shutdown-called")

    slow_func = {'async': slow_task_async, 'thread': slow_task_thread}[execution]

    FuncTask(on_startup, name="startup", on_startup=True, start_cond=true, execution=execution, session=session)
    task = FuncTask(slow_func, name="slow-task", start_cond=true, execution=execution, session=session)
    FuncTask(call_shutdown, name="call-shutdown", start_cond=true, execution=execution, session=session)
    #FuncTask(on_shutdown, name="shutdown", on_shutdown=True, start_cond=true, execution=execution, session=session)


    session.config.shut_cond = TaskStarted(task="call-shutdown") >= 3

    session.start()
    assert timeline == ['startup', 'shutdown-called']
    assert 1 == task.logger.filter_by(action="terminate").count()

@pytest.mark.parametrize("execution", ["main", "thread"])
def test_restart(execution, session):
    timeline = []
    session.config.restarting = 'recall'

    def on_startup():
        timeline.append("startup")

    def call_restart(session:rocketry.Session=Session()):
        session.restart()
        timeline.append("restart-called")

    def on_shutdown():
        timeline.append("shutdown")

    FuncTask(on_startup, name="startup", on_startup=True, execution="main", session=session)
    FuncTask(call_restart, name="restart", start_cond=true, execution=execution, session=session)
    FuncTask(on_shutdown, name="shutdown", on_shutdown=True, execution="main", session=session)

    session.config.shut_cond = (TaskStarted(task="shutdown") >= 2) | ~SchedulerStarted(period=TimeDelta("60 second"))

    session.start()
    assert timeline == ['startup', 'restart-called', 'shutdown', 'startup', 'restart-called', 'shutdown', 'startup', 'shutdown']
