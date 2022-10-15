import logging
import pytest

from task_helpers import wait_till_task_finish

from rocketry.tasks import FuncTask
from rocketry.core.task import Task
from rocketry.exc import TaskInactionException, TaskLoggingError
from rocketry.conditions import AlwaysFalse, AlwaysTrue

Task.use_instance_naming = True


def run_successful_func():
    print("Running func")

def run_failing_func():
    print("Running func")
    raise RuntimeError("Task failed")

def run_inaction():
    raise TaskInactionException()

def run_parametrized(integer, string, optional_float=None):
    assert isinstance(integer, int)
    assert isinstance(string, str)
    assert isinstance(optional_float, float)

def run_parametrized_kwargs(**kwargs):
    assert kwargs
    assert isinstance(kwargs["integer"], int)
    assert isinstance(kwargs["string"], str)
    assert isinstance(kwargs["optional_float"], float)

@pytest.mark.parametrize("execution", ["main", "async", "thread", "process"])
@pytest.mark.parametrize(
    "task_func,expected_outcome,exc_cls",
    [
        pytest.param(
            run_successful_func,
            "success",
            None,
            id="Success"),
        pytest.param(
            run_failing_func,
            "fail",
            RuntimeError,
            id="Failure"),
        pytest.param(
            run_inaction,
            "inaction",
            None,
            id="Inaction"),
    ],
)
def test_run(task_func, expected_outcome, exc_cls, execution, session):
    task = FuncTask(
        task_func,
        name="a task",
        execution=execution,
        session=session
    )

    try:
        task()
    except Exception:
        # failing execution="main"
        if expected_outcome != "fail":
            raise

    # Wait for finish
    wait_till_task_finish(task)

    assert task.status == expected_outcome

    records = list(map(lambda e: e.dict(exclude={'created'}), session.get_task_log()))
    assert [
        {"task_name": "a task", "action": "run"},
        {"task_name": "a task", "action": expected_outcome},
    ] == records


async def run_async_successful():
    ...

async def run_async_fail():
    raise RuntimeError("Failed")

async def run_async_inaction():
    raise TaskInactionException("Did nothing")

@pytest.mark.parametrize("execution", ["main", "async", "thread", "process"])
@pytest.mark.parametrize(
    "task_func,expected_outcome",
    [
        pytest.param(run_async_successful, "success", id="Success"),
        pytest.param(run_async_fail, "fail", id="Failure"),
        pytest.param(run_async_inaction, "inaction", id="Inaction"),
    ],
)
def test_run_async(task_func, expected_outcome, execution, session):

    task = FuncTask(
        task_func,
        name="a task",
        execution=execution,
        session=session
    )

    try:
        task()
    except Exception:
        # failing execution="main"
        if expected_outcome != "fail":
            raise

    # Wait for finish
    wait_till_task_finish(task)

    assert task.status == expected_outcome

    records = list(map(lambda e: e.dict(exclude={'created'}), session.get_task_log()))
    assert [
        {"task_name": "a task", "action": "run"},
        {"task_name": "a task", "action": expected_outcome},
    ] == records

@pytest.mark.parametrize("execution", ["main", "async", "thread", "process"])
@pytest.mark.parametrize(
    "task_func,expected_outcome",
    [
        pytest.param(run_async_successful, "success", id="Success"),
        pytest.param(run_async_fail, "fail", id="Failure"),
        pytest.param(run_async_inaction, "inaction", id="Inaction"),
    ],
)
@pytest.mark.asyncio
async def test_run_log_fail_at_start(task_func, expected_outcome, execution, session):
    class MyHandler(logging.Handler):
        def emit(self, record):
            if record.action == "run":
                raise RuntimeError("Oops")
    logger = logging.getLogger("rocketry.task")
    logger.handlers.insert(0, MyHandler())

    task = FuncTask(
        task_func,
        name="a task",
        execution=execution,
        session=session
    )
    if execution != "thread":
        with pytest.raises(TaskLoggingError):
            await task.start_async()
    else:
        await task.start_async()
        assert task._run_stack[0].exception
    # Wait for finish
    await session.scheduler.wait_task_alive()
    session.scheduler.handle_logs()

    # At the moment the run log is not propagated to
    # finish
    assert task.status != "run"

@pytest.mark.parametrize("execution", ["main", "async", "thread", "process"])
@pytest.mark.parametrize(
    "task_func,expected_outcome",
    [
        pytest.param(run_async_successful, "success", id="Success"),
        pytest.param(run_async_fail, "fail", id="Failure"),
        pytest.param(run_async_inaction, "inaction", id="Inaction"),
    ],
)
@pytest.mark.asyncio
async def test_run_log_fail_at_end(task_func, expected_outcome, execution, session):
    class MyHandler(logging.Handler):
        def emit(self, record):
            if record.action != "run":
                raise RuntimeError("Oops")
    logger = logging.getLogger("rocketry.task")
    logger.handlers.insert(0, MyHandler())

    task = FuncTask(
        task_func,
        name="a task",
        execution=execution,
        session=session
    )
    if execution == "main":
        with pytest.raises(TaskLoggingError):
            await task.start_async()
    else:
        await task.start_async()

    await session.scheduler.wait_task_alive()

    if execution == "process":
        with pytest.raises(TaskLoggingError):
            session.scheduler.handle_logs()
    assert task.status == "fail"

def test_force_run(session):

    task = FuncTask(
        run_successful_func,
        name="task",
        start_cond=AlwaysFalse(),
        execution="main",
        session=session
    )
    with pytest.deprecated_call():
        task.force_run = True

    assert bool(task)
    assert bool(task)

    task()
    assert not task.force_run


def test_dependency(tmpdir, session):

    task_a = FuncTask(
        run_successful_func,
        name="task_a",
        start_cond=AlwaysTrue(),
        execution="main",
        session=session
    )
    task_b = FuncTask(
        run_successful_func,
        name="task_b",
        start_cond=AlwaysTrue(),
        execution="main",
        session=session
    )
    task_dependent = FuncTask(
        run_successful_func,
        name="task_dependent",
        start_cond="after task 'task_a' & after task 'task_b'",
        execution="main",
        session=session
    )
    assert not bool(task_dependent)
    task_a()
    assert not bool(task_dependent)
    task_b()
    assert bool(task_dependent)


# Parametrization
def test_parametrization_runtime(session):

    task = FuncTask(
        run_parametrized,
        name="a task",
        execution="main",
        session=session
    )

    task(params={"integer": 1, "string": "X", "optional_float": 1.1, "extra_parameter": "Should not be passed"})

    records = list(map(lambda e: e.dict(exclude={'created'}), session.get_task_log()))
    assert [
        {"task_name": "a task", "action": "run"},
        {"task_name": "a task", "action": "success"},
    ] == records

def test_parametrization_local(session):

    task = FuncTask(
        run_parametrized,
        name="a task",
        parameters={"integer": 1, "string": "X", "optional_float": 1.1},
        execution="main",
        session=session
    )

    task()

    records = list(map(lambda e: e.dict(exclude={'created'}), session.get_task_log()))
    assert [
        {"task_name": "a task", "action": "run"},
        {"task_name": "a task", "action": "success"},
    ] == records

def test_parametrization_kwargs(session):

    task = FuncTask(
        run_parametrized_kwargs,
        name="a task",
        parameters={"integer": 1, "string": "X", "optional_float": 1.1},
        execution="main",
        session=session
    )

    task()

    records = list(map(lambda e: e.dict(exclude={'created'}), session.get_task_log()))
    assert [
        {"task_name": "a task", "action": "run"},
        {"task_name": "a task", "action": "success"},
    ] == records
