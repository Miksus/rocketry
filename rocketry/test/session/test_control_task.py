import pytest
from rocketry.args.builtin import SimpleArg
from rocketry.conditions.task.task import TaskStarted
from rocketry.core.parameters.parameters import Parameters
from rocketry.tasks import FuncTask
from rocketry.conditions import SchedulerCycles, AlwaysFalse

def run_succeeding():
    pass

def run_parametrized(arg=SimpleArg("incorrect")):
    assert arg == "correct"

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_set_running(execution, session):
    task = FuncTask(
        run_succeeding,
        start_cond=AlwaysFalse(),
        name="task",
        execution=execution,
        session=session
    )
    assert task.batches == []
    task.run()
    assert task.batches == [Parameters()]

    session.config.shut_cond = SchedulerCycles() >= 5
    session.start()

    logger = task.logger
    assert 1 == logger.filter_by(action="run").count()
    assert 1 == logger.filter_by(action="success").count()
    assert 0 == logger.filter_by(action="fail").count()

    assert len(task.batches) == 0

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_set_running_with_params(execution, session):
    task = FuncTask(
        run_parametrized,
        start_cond=AlwaysFalse(),
        name="task",
        execution=execution,
        session=session
    )
    task.run(arg="correct")
    task.run(arg="correct")
    task.run(arg="incorrect")
    assert task.batches == [
        Parameters({"arg": "correct"}), Parameters({"arg": "correct"}), Parameters({"arg": "incorrect"})
    ]

    session.config.shut_cond = TaskStarted(task=task) == 3
    session.start()

    logger = task.logger
    assert 3 == logger.filter_by(action="run").count()
    assert 2 == logger.filter_by(action="success").count()
    assert 1 == logger.filter_by(action="fail").count()

    assert len(task.batches) == 0

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_set_running_disabled(execution, session):
    # NOTE: force_run overrides disabled
    # as it is more practical to keep
    # a task disabled and force it running
    # manually than prevent force run with
    # disabling
    task = FuncTask(
        run_succeeding,
        start_cond=AlwaysFalse(),
        name="task",
        execution=execution,
        session=session
    )
    task.disabled = True
    task.run()

    session.config.shut_cond = SchedulerCycles() >= 5
    session.start()
    assert task.batches == []

    logger = task.logger
    assert 1 == logger.filter_by(action="run").count()
    assert 1 == logger.filter_by(action="success").count()

    assert task.disabled

# Deprecated
# ----------

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_task_force_run(execution, session):
    task = FuncTask(
        run_succeeding,
        start_cond=AlwaysFalse(),
        name="task",
        execution=execution,
        session=session
    )
    with pytest.warns(DeprecationWarning):
        task.force_run = True

    session.config.shut_cond = SchedulerCycles() >= 5
    session.start()

    logger = task.logger
    assert 1 == logger.filter_by(action="run").count()

    # The force_run should have reseted as it should have run once
    assert not task.force_run

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_task_force_disabled(execution, session):
    # NOTE: force_run overrides disabled
    # as it is more practical to keep
    # a task disabled and force it running
    # manually than prevent force run with
    # disabling
    task = FuncTask(
        run_succeeding,
        start_cond=AlwaysFalse(),
        name="task",
        execution=execution,
        session=session
    )
    task.disabled = True
    with pytest.warns(DeprecationWarning):
        task.force_run = True

    session.config.shut_cond = SchedulerCycles() >= 5
    session.start()
    assert task.batches == []

    logger = task.logger
    assert 1 == logger.filter_by(action="run").count()
    assert 1 == logger.filter_by(action="success").count()

    assert task.disabled
    assert not task.force_run # This should be reseted
