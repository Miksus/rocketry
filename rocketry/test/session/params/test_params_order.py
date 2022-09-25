
from pathlib import Path
from textwrap import dedent
import pytest
from rocketry.args.builtin import SimpleArg
from rocketry.core.condition.base import AlwaysTrue
from rocketry.tasks import FuncTask
from rocketry.conditions import SchedulerCycles

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

@pytest.mark.parametrize("delayed", [True, False])
@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_task_favored(execution, session, tmpdir, delayed):
    # task params > func params > session params
    session.parameters['arg'] = 'incorrect'

    if delayed:
        funcfile = tmpdir.join("script_task_favored.py")
        funcfile.write(dedent("""
            from rocketry.args import SimpleArg
            def run_parametrized_incorrect(arg=SimpleArg("incorrect")):
                assert arg == "correct"
        """))
        task = FuncTask(
            path=Path(funcfile), func_name="run_parametrized_incorrect",
            start_cond=AlwaysTrue(),
            name="task",
            execution=execution,
            session=session,
            parameters={"arg": "correct"}
        )
    else:
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
