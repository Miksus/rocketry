from pathlib import Path
import platform
from textwrap import dedent
import pytest

from rocketry.core import Parameters
from rocketry.tasks import FuncTask
from rocketry.conditions import TaskStarted, AlwaysTrue
from rocketry.args import FuncArg, Arg


def get_x():
    return "x"

def get_y():
    return "y"

def func_x_with_arg(myparam):
    assert myparam == "x"

def func_with_embed_arg(myparam=Arg('value_x')):
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
        start_cond=AlwaysTrue(),
        session=session
    )
    session.config.shut_cond = (TaskStarted(task="a task") >= 1)

    assert task.status is None
    session.start()

    assert "success" == task.status

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_embedded(session, execution):

    task = FuncTask(
        func_with_embed_arg,
        execution=execution,
        name="a task",
        start_cond=AlwaysTrue(),
        session=session
    )
    assert task.parameters == Parameters(myparam=Arg('value_x'))
    session.parameters["value_x"] = "x"
    session.config.shut_cond = (TaskStarted(task="a task") >= 1)

    assert task.status is None
    session.start()
    assert task.parameters == Parameters(myparam=Arg('value_x'))

    assert "success" == task.status

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_embedded_script(session, execution, tmpdir):

    funcfile = tmpdir.join("script_embedded_params.py")
    funcfile.write(dedent("""
        from rocketry.args import Arg
        def main(myparam=Arg('value_x')):
            assert myparam == 'x'
    """))

    task = FuncTask(
        path=Path(funcfile),
        func_name="main",
        execution=execution,
        name="a task",
        start_cond=AlwaysTrue(),
        session=session
    )
    assert task.parameters == Parameters()
    session.parameters["value_x"] = "x"
    session.config.shut_cond = (TaskStarted(task="a task") >= 1)

    assert task.status is None
    session.start()
    assert task.parameters == Parameters()

    assert "success" == task.status

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_session(session, execution):

    session.parameters["myparam"] = FuncArg(get_x)

    task = FuncTask(
        func_x_with_arg,
        execution=execution,
        name="a task",
        start_cond=AlwaysTrue(),
        session=session
    )
    session.config.shut_cond = (TaskStarted(task="a task") >= 1)

    assert task.status is None
    session.start()

    assert "success" == task.status

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_session_with_arg(session, execution):

    session.parameters["a_param"] = FuncArg(get_x)

    task = FuncTask(
        func_x_with_arg,
        execution=execution,
        name="a task",
        parameters={"myparam": Arg('a_param')},
        start_cond=AlwaysTrue(),
        session=session
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
        session.config.param_materialize = config_mater

    session.parameters["session_arg"] = "z"
    session.parameters["myparam"] = FuncArg(get_with_nested_args, materialize=materialize)

    task = FuncTask(
        func_x_with_arg,
        execution=execution,
        name="a task",
        start_cond=AlwaysTrue(),
        session=session
    )
    session.config.shut_cond = (TaskStarted(task="a task") >= 1)

    assert task.status is None
    session.start()
    if platform.system() == "Windows" and execution == "process" and (materialize == "post" or (materialize is None and config_mater in ("post", None))):
        # Windows cannot pickle the session but apparently Linux can
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
        start_cond=AlwaysTrue(),
        session=session
    )

    session.config.shut_cond = (TaskStarted(task="a task") >= 1)

    assert task.status is None
    session.start()
    assert "success" == task.status
