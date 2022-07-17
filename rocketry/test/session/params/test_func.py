
import pytest

from rocketry.args import Private, Return
from rocketry import Scheduler
from rocketry.conditions.scheduler import SchedulerCycles
from rocketry.core import parameters
from rocketry.tasks import FuncTask
from rocketry.conditions import TaskStarted, AlwaysTrue
from rocketry.args import FuncArg, Arg


def get_x():
    return "x"

def get_y():
    return "y"

def func_x_with_arg(myparam):
    assert myparam == "x"

def get_with_nested_args(arg = FuncArg(get_y), arg_2 = Arg('session_arg')):
    assert arg == "y"
    assert arg_2 == "z"
    return 'x'

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_simple(session, execution):

    task = FuncTask(
        func_x_with_arg, 
        parameters={"myparam": FuncArg(get_x)}, 
        execution=execution, 
        name="a task", 
        start_cond=AlwaysTrue()
    )
    session.config.shut_cond = (TaskStarted(task="a task") >= 1)

    assert task.status is None
    session.start()

    assert "success" == task.status

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_session(session, execution):

    session.parameters["myparam"] = FuncArg(get_x)

    task = FuncTask(
        func_x_with_arg, 
        execution=execution, 
        name="a task", 
        start_cond=AlwaysTrue()
    )
    session.config.shut_cond = (TaskStarted(task="a task") >= 1)

    assert task.status is None
    session.start()

    assert "success" == task.status

@pytest.mark.parametrize("config_mater", ['pre', 'post', None])
@pytest.mark.parametrize("materialize", ['pre', 'post', None])
@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_nested(session, execution, materialize, config_mater):
    if config_mater is not None:
        session.config.func_param_materialize = config_mater

    session.parameters["session_arg"] = "z"
    session.parameters["myparam"] = FuncArg(get_with_nested_args, materialize=materialize)

    task = FuncTask(
        func_x_with_arg, 
        execution=execution, 
        name="a task", 
        start_cond=AlwaysTrue()
    )
    session.config.shut_cond = (TaskStarted(task="a task") >= 1)

    assert task.status is None
    session.start()
    if execution == "process" and (materialize == "post" or (materialize is None and config_mater in ("post", None))):
        assert "fail" == task.status
    else:
        assert "success" == task.status

class UnPicklable:
    def __getstate__(self):
        raise RuntimeError("Cannot be pickled")

def get_unpicklable():
    return UnPicklable()

def func_check_unpicklable(myparam):
    assert isinstance(myparam, UnPicklable)

@pytest.mark.parametrize("execution", ["process"])
def test_unpicklable(session, execution):
    "Test a FuncArg that returns unpicklable item"
    task = FuncTask(
        func_check_unpicklable, 
        parameters={"myparam": FuncArg(get_unpicklable)}, 
        execution=execution, 
        name="a task", 
        start_cond=AlwaysTrue()
    )

    session.config.shut_cond = (TaskStarted(task="a task") >= 1) 

    assert task.status is None
    session.start()
    assert "success" == task.status