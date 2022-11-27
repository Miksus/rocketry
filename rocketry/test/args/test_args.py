import os
import sys
import logging
import pytest
from rocketry.args import Private, SimpleArg, FuncArg, Arg, EnvArg, CliArg, Return, TerminationFlag, Task, Session, TaskLogger, SchedulerLogger, Config
from rocketry.core.log.adapter import TaskAdapter
from rocketry.core.parameters.parameters import Parameters
from rocketry.tasks import FuncTask

def test_simple():
    arg = SimpleArg("a value")
    assert arg.get_value() == "a value"

def test_func():
    def get_value():
        return 'a value'

    arg = FuncArg(get_value)
    assert arg.get_value() == "a value"

def test_arg(session):

    session.parameters['myarg'] = 'a value'
    arg = Arg('myarg')
    assert arg.get_value(session=session) == "a value"

    assert Arg('missing', default="a value").get_value(session=session) == "a value"
    with pytest.raises(KeyError):
        arg = Arg('missing')
        arg.get_value(session=session)

def test_env_arg():
    os.environ['ROCKETRY_TEST_VARIABLE'] = "a value"
    arg = EnvArg('ROCKETRY_TEST_VARIABLE')
    assert arg.get_value() == "a value"

    arg = EnvArg('ROCKETRY_NOT_SET', default="a value 2")
    assert arg.get_value() == "a value 2"

    with pytest.raises(KeyError):
        arg = EnvArg('ROCKETRY_NOT_SET')
        arg.get_value()

def test_cli_arg():
    assert CliArg.cli_args == sys.argv
    orig_arg = CliArg.cli_args
    try:
        CliArg.cli_args = ['python', 'myfile.py', '--myparam', 'a value']

        arg = CliArg('--myparam')
        assert arg.get_value() == "a value"
        assert CliArg('--invalid', default="a value").get_value() == "a value"
        with pytest.raises(KeyError):
            CliArg('--invalid').get_value()
    finally:
        CliArg.cli_args = orig_arg

def test_return(session):
    runned = FuncTask(lambda x: x, name="runned", session=session)
    unrunned = FuncTask(lambda x: x, name="unrunned", session=session)

    session.returns[runned] = 'a value'

    assert Return("runned").get_value(session=session) == "a value"
    assert Return(runned).get_value(session=session) == "a value"
    assert Return("unrunned", default="a value").get_value(session=session) == "a value"
    assert Return(unrunned, default="a value").get_value(session=session) == "a value"

    with pytest.raises(ValueError):
        Return("non_existent").get_value(session=session)

    with pytest.raises(KeyError):
        Return("unrunned").get_value(session=session)

def test_private(session):
    task = FuncTask(lambda x: x, session=session)

    value = Private("my secret")
    assert value.get_value() == "*****"
    assert value.get_value(task=task) == "my secret"
    assert str(value) == "*****"
    assert repr(value) == "Private(*****)"

# Component Args
# --------------

def test_session(session):
    with pytest.raises(TypeError):
        Session().get_value()
    assert Session(default=None).get_value() is None
    assert Session().get_value(session=session) is session

    task_1 = FuncTask(
        lambda : None,
        name="task 1",
        execution="main",
        session=session
    )
    assert Session().get_value(task=task_1) is session
    assert Session().get_value(scheduler=session.scheduler) is session

def test_config(session):
    p = Parameters(config=Config())
    assert p.materialize(session=session)['config'] is session.config

def test_task(session):
    task_1 = FuncTask(
        lambda : None,
        name="task 1",
        execution="main",
        session=session
    )
    task_2 = FuncTask(
        lambda : None,
        name="task 2",
        execution="main",
        session=session
    )
    assert Task().get_value(task=task_1) is task_1
    assert Task().get_value(task=task_1, session=session) is task_1
    assert Task("task 1").get_value(session=session) is task_1
    assert Task("task 1").get_value(session=session, task=task_2) is task_1

    with pytest.raises(KeyError):
        assert Task("task 3").get_value(session=session)
    with pytest.raises(TypeError):
        Task().get_value()
    with pytest.raises(TypeError):
        Task().get_value(task="not valid")

    assert Task(default=None).get_value() is None

    # Test materialization
    assert Parameters(t=Task("task 1")).materialize(session=session)['t'] is task_1
    assert Parameters(t=Task("task 1")).materialize(task=task_2)['t'] is task_1

def test_task_logger(session):
    task_1 = FuncTask(
        lambda : None,
        name="task 1",
        execution="main",
        session=session
    )
    logger = TaskLogger().get_value(task=task_1, session=session)
    assert isinstance(logger, TaskAdapter)
    assert logger.task_name == "task 1"
    assert logger.name == "rocketry.task"

    p = Parameters(logger=TaskLogger())
    assert isinstance(p.materialize(session=session)['logger'], TaskAdapter)

def test_scheduler_logger(session):
    logger = SchedulerLogger().get_value(session=session)
    assert logger.name == "rocketry.scheduler"
    assert isinstance(logger, logging.Logger)

# Magic
# -----

@pytest.mark.parametrize("obj", [Arg('x'), SimpleArg('value'), Private('value'), FuncArg(lambda: None), Return('a_task'), TerminationFlag()])
def test_no_errors(obj, session):
    task = FuncTask(lambda: None, name="a_task", session=session)
    session.returns[task] = None
    session.parameters['x'] = None
    obj.get_value(dont_use="something", session=session, task=task)
    str(obj)
    repr(obj)
