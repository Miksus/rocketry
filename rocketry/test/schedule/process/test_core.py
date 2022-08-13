
import multiprocessing

from rocketry.core import Scheduler
from rocketry.tasks import FuncTask
from rocketry.time import TimeDelta
from rocketry.conditions import SchedulerStarted, TaskStarted, AlwaysTrue

def run_succeeding():
    pass

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
