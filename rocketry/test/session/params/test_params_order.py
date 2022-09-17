
import pytest
from rocketry.args.builtin import SimpleArg
from rocketry.conditions.task.task import TaskStarted
from rocketry.core.condition.base import AlwaysTrue
from rocketry.core.parameters.parameters import Parameters
from rocketry.tasks import FuncTask
from rocketry.conditions import SchedulerCycles, AlwaysFalse
from rocketry.args import Private, TerminationFlag

def run_parametrized(arg):
    assert arg == "correct"

def run_parametrized_correct(arg=SimpleArg('correct')):
    assert arg == "correct"

def run_parametrized_incorrect(arg=SimpleArg("incorrect")):
    assert arg == "correct"

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_batch_favored(execution, session):
    # batch params > task params > func params > session params
    session.parameters['arg'] = 'incorrect'

    task = FuncTask(
        run_parametrized_incorrect, 
        start_cond=AlwaysTrue(), 
        name="task",
        execution=execution,
        session=session,
        parameters={"arg": "incorrect"}
    )
    task.run(arg="correct")
    session.config.shut_cond = SchedulerCycles() == 1
    session.start()

    logger = task.logger
    assert 1 == logger.filter_by(action="run").count()
    assert 1 == logger.filter_by(action="success").count()

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_task_favored(execution, session):
    # task params > func params > session params
    session.parameters['arg'] = 'incorrect'

    task = FuncTask(
        run_parametrized_incorrect, 
        start_cond=AlwaysTrue(), 
        name="task",
        execution=execution,
        session=session,
        parameters={"arg": "correct"}
    )
    session.config.shut_cond = SchedulerCycles() == 1
    session.start()

    logger = task.logger
    assert 1 == logger.filter_by(action="run").count()
    assert 1 == logger.filter_by(action="success").count()

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_func_favored(execution, session):
    # func params > session params
    session.parameters['arg'] = 'incorrect'

    task = FuncTask(
        run_parametrized_correct, 
        start_cond=AlwaysTrue(), 
        name="task",
        execution=execution,
        session=session,
    )
    session.config.shut_cond = SchedulerCycles() == 1
    session.start()

    logger = task.logger
    assert 1 == logger.filter_by(action="run").count()
    assert 1 == logger.filter_by(action="success").count()

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_session_favored(execution, session):
    # session params
    session.parameters['arg'] = 'correct'

    task = FuncTask(
        run_parametrized, 
        start_cond=AlwaysTrue(), 
        name="task",
        execution=execution,
        session=session,
    )
    session.config.shut_cond = SchedulerCycles() == 1
    session.start()

    logger = task.logger
    assert 1 == logger.filter_by(action="run").count()
    assert 1 == logger.filter_by(action="success").count()