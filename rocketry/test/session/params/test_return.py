import pytest

from rocketry.args import Return
from rocketry.conditions.scheduler import SchedulerCycles
from rocketry.core import Parameters
from rocketry.tasks import FuncTask
from rocketry.conditions import TaskStarted


def func_with_arg(value):
    pass

def func_x_with_return():
    return "x"

def func_x_with_arg(myparam):
    assert myparam == "x"


@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_normal(session, execution):

    task_return = FuncTask(
        func_x_with_return,
        name="return task",
        start_cond="~has started",
        execution=execution,
        session=session
    )
    task_return.run()
    task = FuncTask(
        func_x_with_arg,
        name="a task",
        start_cond="after task 'return task'",
        parameters={"myparam": Return('return task')},
        execution=execution,
        session=session
    )

    assert task.status is None

    session.config.shut_cond = TaskStarted(task="a task") >= 1
    session.start()

    assert dict(session.returns) == {task_return: "x", task: None}
    assert "success" == task_return.status
    assert "success" == task.status

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_normal_pass_task(session, execution):

    task_return = FuncTask(
        func_x_with_return,
        name="return task",
        start_cond="~has started",
        execution=execution,
        session=session
    )
    task_return.run()
    task = FuncTask(
        func_x_with_arg,
        name="a task",
        start_cond="after task 'return task'",
        parameters={"myparam": Return(task_return)},
        execution=execution,
        session=session
    )

    assert task.status is None

    session.config.shut_cond = TaskStarted(task="a task") >= 1
    session.start()

    assert dict(session.returns) == {task_return: "x", task: None}
    assert "success" == task_return.status
    assert "success" == task.status

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_normal_pass_func(session, execution):
    # This use case is for using the app pattern
    @FuncTask(
        name="return task",
        start_cond="~has started",
        execution="main",
        batches=[Parameters()],
        session=session
    )
    def func_with_arg_local():
        return 'x'

    task = FuncTask(
        func_x_with_arg,
        name="a task",
        start_cond="after task 'return task'",
        parameters={"myparam": Return(func_with_arg_local)},
        execution=execution,
        session=session,
    )

    assert task.status is None

    session.config.shut_cond = (TaskStarted(task="a task") >= 1) | (SchedulerCycles() >= 5)
    session.start()

    task_return = session["return task"]
    assert dict(session.returns) == {task_return: "x", task: None}
    assert "success" == task_return.status
    assert "success" == task.status

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_missing(session, execution):
    session.config.silence_task_prerun = True # Default in prod

    task = FuncTask(
        func_with_arg,
        parameters={"myparam": Return('return task')},
        name="a task",
        execution=execution,
        session=session
    )
    task.run()
    assert task.status is None
    session.config.shut_cond = TaskStarted(task="a task") >= 1
    session.start()

    assert "fail" == task.status

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_default(session, execution):
    task = FuncTask(
        func_with_arg,
        name="return task",
        session=session
    )
    task = FuncTask(
        func_x_with_arg,
        parameters={"myparam": Return('return task', default="x")},
        name="a task",
        execution=execution,
        session=session
    )
    task.run()

    assert task.status is None
    session.config.shut_cond = TaskStarted(task="a task") >= 1
    session.start()

    assert "success" == task.status
