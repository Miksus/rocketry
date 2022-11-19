
import threading
from time import sleep
import pytest
import rocketry
from rocketry.conditions import DependSuccess
from rocketry.exc import TaskTerminationException


from rocketry.tasks import FuncTask
from rocketry.time import TimeDelta
from rocketry.conditions import SchedulerCycles, SchedulerStarted, TaskStarted, AlwaysTrue

from rocketry.args import Arg, Return, Session, Task, FuncArg, TerminationFlag #, Param, Session

# Example functions
# -----------------
def get_some_value():
    return 'some func value'

def get_some_value_with_arg(pass_yes):
    assert pass_yes == 'yes'
    return 'some func value 2'

# Example task functions
# ----------------------

def run_with_output():
    return 'some value'

def run_with_func_arg(arg=FuncArg(get_some_value), arg2=FuncArg(get_some_value_with_arg, pass_yes='yes')):
    assert arg == 'some func value'
    assert arg2 == 'some func value 2'

def run_with_session_arg(arg=Arg('my_arg')):
    assert arg == 'some session value'

def run_with_return(arg=Return('task_with_output')):
    assert arg == 'some value'

def run_with_task(arg = Task(), arg2 = Task('another_task')):
    # arg should be the task itself, arg2 another task
    assert isinstance(arg, rocketry.core.Task)
    assert isinstance(arg2, rocketry.core.Task)
    assert arg.name == 'my_task'
    assert arg2.name == 'another_task'

def run_with_session(arg=Session()):
    assert isinstance(arg, rocketry.Session)
    assert arg.parameters['my_arg'] == 'some session value'

def run_with_termination_flag(flag=TerminationFlag(), task=Task()):
    if task.execution == "process":
        return
    assert isinstance(flag, threading.Event), f"Flag incorrect type: {type(flag)}"
    assert not flag.is_set()

    if task.execution == "main":
        return

    waited = 0
    while True:
        if flag.is_set():
            raise TaskTerminationException("Flag raised")

        sleep(0.001)
        waited += 0.001
        if waited > 1:
            raise RuntimeError("Did not terminate")

# Tests
# -----

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_func_arg(execution, session):
    task = FuncTask(func=run_with_func_arg, start_cond=AlwaysTrue(), execution=execution, session=session)

    session.config.shut_cond = (SchedulerCycles() >= 1) | ~SchedulerStarted(period=TimeDelta("20 seconds"))
    session.start()

    logger = task.logger
    assert 1 == logger.filter_by(action="run").count()
    assert 1 == logger.filter_by(action="success").count()
    assert 0 == logger.filter_by(action="fail").count()

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_session_arg(execution, session):
    task = FuncTask(func=run_with_session_arg, start_cond=AlwaysTrue(), execution=execution, session=session)

    session.config.shut_cond = (SchedulerCycles() >= 1) | ~SchedulerStarted(period=TimeDelta("20 seconds"))
    session.parameters['my_arg'] = 'some session value'
    session.start()

    logger = task.logger
    assert 1 == logger.filter_by(action="run").count()
    assert 1 == logger.filter_by(action="success").count()
    assert 0 == logger.filter_by(action="fail").count()

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_return(execution, session):

    input_task = FuncTask(func=run_with_output, name="task_with_output", start_cond=(TaskStarted(task="task_with_output") == 0), execution=execution, session=session)
    task = FuncTask(func=run_with_return, name="task_use_output", start_cond=DependSuccess(depend_task=input_task), execution=execution, session=session)

    session.config.shut_cond = (TaskStarted(task="task_use_output") >= 1) | ~SchedulerStarted(period=TimeDelta("10 seconds"))
    session.start()

    logger = task.logger
    assert 1 == logger.filter_by(action="run").count()
    assert 1 == logger.filter_by(action="success").count()
    assert 0 == logger.filter_by(action="fail").count()

    logger = input_task.logger
    assert 1 == logger.filter_by(action="run").count()
    assert 1 == logger.filter_by(action="success").count()
    assert 0 == logger.filter_by(action="fail").count()

    assert session.returns[input_task] == 'some value'

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_session_as_arg(execution, session):
    task = FuncTask(func=run_with_session, start_cond=AlwaysTrue(), execution=execution, session=session)

    session.config.shut_cond = (SchedulerCycles() >= 1) | ~SchedulerStarted(period=TimeDelta("20 seconds"))
    session.parameters['my_arg'] = 'some session value'
    session.start()

    logger = task.logger
    assert 1 == logger.filter_by(action="run").count()
    assert 1 == logger.filter_by(action="success").count()
    assert 0 == logger.filter_by(action="fail").count()

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_task_as_arg(execution, session):
    another_task = FuncTask(func=run_with_output, name="another_task", session=session)
    task = FuncTask(func=run_with_task, name="my_task", start_cond=AlwaysTrue(), execution=execution, session=session)

    session.config.shut_cond = (SchedulerCycles() >= 1) | ~SchedulerStarted(period=TimeDelta("20 seconds"))
    session.start()

    logger = task.logger
    assert 1 == logger.filter_by(action="run").count()
    assert 1 == logger.filter_by(action="success").count()
    assert 0 == logger.filter_by(action="fail").count()

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_termination_flag_as_arg(execution, session):
    if execution == "process":
        pytest.skip("For some reason CI fails on process. Termination flag should not be used with process tasks anyways.")

    task = FuncTask(func=run_with_termination_flag, name="my_task", start_cond=AlwaysTrue(), execution=execution, session=session)

    @FuncTask(name="terminator", execution="main", start_cond="task 'my_task' has started", session=session)
    def task_terminate(session=Session()):
        session["my_task"].terminate()

    session.config.shut_cond = (TaskStarted(task="my_task") >= 1) | ~SchedulerStarted(period=TimeDelta("20 seconds"))

    if execution in ("main", "process"):
        with pytest.warns(UserWarning):
            session.start()
    else:
        session.start()

    logger = task.logger
    assert 1 == logger.filter_by(action="run").count()
    if execution == "thread":
        assert 1 == logger.filter_by(action="terminate").count()
    else:
        assert 1 == logger.filter_by(action="success").count()
