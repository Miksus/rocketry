from pathlib import Path
import types

import pytest

from rocketry.tasks import FuncTask
from rocketry.conditions import AlwaysTrue
from rocketry.parse.utils import ParserError

def myfunc():
    ...

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_construct(tmpdir, session, execution):

    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd():
        if execution == "process":
            with pytest.raises(AttributeError):
                # Unpicklable function (cannot use process)
                task = FuncTask(lambda : None, execution=execution, session=session)
        else:
            task = FuncTask(lambda : None, execution=execution, session=session)

        # This should always be picklable
        task = FuncTask(myfunc, execution=execution, session=session)
        assert not task.is_delayed()
        assert task.status is None

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_construct_callable_class(tmpdir, session, execution):
    class MyClass:
        def __call__(self):
            pass

    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd():
        # This should always be picklable
        task = FuncTask(MyClass(), execution=execution, session=session)
        assert not task.is_delayed()
        assert task.status is None
        assert task.name.endswith("test_construct:MyClass")

def test_description(session):
    "Test Task.description is correctly set (uses the func if missing)"

    # Test no description
    task = FuncTask(name="no desc 1", session=session)
    @task
    def myfunc():
        ...
    assert task.description is None

    task = FuncTask(lambda x: x, name="no desc 2", execution="main", session=session)
    assert task.description is None


     # Test description from doc (decorated)
    task = FuncTask(name="has desc 1", session=session)
    @task
    def myfunc():
        "This is func"
    assert task.description == "This is func"

    # Test description from doc (normal)
    def myfunc():
        "This is func"
    task = FuncTask(myfunc, name="has desc 2", session=session)
    assert task.description == "This is func"

    # Test the description is respected if doc is found
    def myfunc():
        "This is func"
    task = FuncTask(myfunc, name="has desc 3", description="But this is preferred", session=session)
    assert task.description == "But this is preferred"

    # Test the description is respected if doc missing
    def myfunc():
        ...
    task = FuncTask(myfunc, name="has desc 4", description="This is func", session=session)
    assert task.description == "This is func"

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_construct_delayed(session, execution, tmpdir):
    tmpdir.join("myfile.py").write("")
    with tmpdir.as_cwd():
        with pytest.warns(UserWarning):
            task = FuncTask(func_name="myfunc", path="missing.py", execution=execution, session=session)
        task = FuncTask(func_name="myfunc", path="myfile.py", execution=execution, session=session)
        assert task.status is None
        assert task.is_delayed()
        assert task.func_name == "myfunc"
        assert task.path == Path("myfile.py")
        assert task.func is None

def test_construct_decorate(session):
    @FuncTask(start_cond=AlwaysTrue(), name="mytask", execution="main", session=session)
    def do_stuff():
        pass

    assert isinstance(do_stuff, types.FunctionType)

    do_stuff_task = session["mytask"]
    assert isinstance(do_stuff_task, FuncTask)
    assert do_stuff_task.status is None
    assert do_stuff_task.start_cond == AlwaysTrue()
    assert do_stuff_task.name == "mytask"

    assert {do_stuff_task} == session.tasks

def test_construct_decorate_minimal(session):
    """This is an exception when FuncTask returns itself
    (__init__ cannot return anything else)"""
    # Going to tempdir to dump the log files there
    session.config.execution = 'main'

    with pytest.warns(UserWarning):
        @FuncTask
        def do_stuff():
            pass

    assert set() == session.tasks

def test_construct_decorate_default_name(session):

    @FuncTask(start_cond=AlwaysTrue(), execution="main", session=session)
    def do_stuff():
        pass

    assert isinstance(do_stuff, types.FunctionType)
    do_stuff_task = list(session.tasks)[-1]
    assert isinstance(do_stuff_task, FuncTask)
    assert do_stuff_task.status is None
    assert do_stuff_task.start_cond == AlwaysTrue()
    assert do_stuff_task.name.endswith(":do_stuff")

    assert [do_stuff_task] == list(session.tasks)

@pytest.mark.parametrize(
    "start_cond,depend,expected",
    [
        pytest.param(
            AlwaysTrue(),
            None,
            AlwaysTrue(),
            id="AlwaysTrue"),
    ],
)
def test_set_start_condition(start_cond, depend, expected, session):

    task = FuncTask(
        lambda : None,
        name="task",
        start_cond=start_cond,
        execution="main",
        session=session
    )
    assert expected == task.start_cond


@pytest.mark.parametrize(
    "start_cond_str,start_cond",
    [
        pytest.param("true", lambda: AlwaysTrue(), id="true"),
        pytest.param("always true & always true", lambda: AlwaysTrue() & AlwaysTrue(), id="always true & always true"),
    ],
)
def test_set_start_condition_str(start_cond_str, start_cond, session):

    task = FuncTask(
        lambda : None,
        name="task",
        start_cond=start_cond_str,
        execution="main",
        session=session
    )
    assert start_cond() == task.start_cond

    assert str(task.start_cond) == start_cond_str

@pytest.mark.parametrize(
    "get_task,exc",
    [
        pytest.param(
            lambda s: FuncTask(lambda : None, name="task", start_cond="this is not valid", execution="main", session=s),
            ParserError,
            id="invalid start_cond"
        ),
        pytest.param(
            lambda s: FuncTask(lambda : None, name="task", execution="not valid", session=s),
            ValueError,
            id="invalid execution"
        ),
    ],
)
def test_failure(session, exc, get_task):
    with pytest.raises(exc):
        get_task(session)
    assert session.tasks == set()

def test_rename(session):
    task1 = FuncTask(lambda : None, name="a task 1", execution="main", session=session)
    task2 = FuncTask(lambda : None, name="a task 2", execution="main", session=session)
    assert session.tasks == {task1, task2}
    assert 'renamed task' not in session
    assert 'a task 1' in session

    task1.name = "renamed task"
    assert task1.name == "renamed task"
    assert session.tasks == {task1, task2}
    assert 'renamed task' in session
    assert 'a task 1' not in session

def test_rename_conflict(session):
    task1 = FuncTask(lambda : None, name="a task 1", execution="main", session=session)
    task2 = FuncTask(lambda : None, name="a task 2", execution="main", session=session)
    assert session.tasks == {task1, task2}
    assert 'renamed task' not in session
    assert 'a task 1' in session

    with pytest.raises(ValueError):
        task1.name = "a task 2"
    assert session.tasks == {task1, task2}
    assert session['a task 2'] is task2
    assert session['a task 2'] is not task1

def test_existing_raise(session):
    assert session.config.task_pre_exist == 'raise'

    task1 = FuncTask(lambda : None, name="a task", execution="main", session=session)
    with pytest.raises(ValueError):
        task2 = FuncTask(lambda : None, name="a task", execution="main", session=session)
    assert session.tasks == {task1}

def test_existing_ignore(session):
    session.config.task_pre_exist = 'ignore'
    task1 = FuncTask(lambda : None, name="a task", execution="main", session=session)
    task2 = FuncTask(lambda : None, name="a task", execution="main", session=session)
    assert session.tasks == {task1}

@pytest.mark.skip(reason="No support for this yet")
def test_existing_replace(session):
    session.config.task_pre_exist = 'replace'
    task1 = FuncTask(lambda : None, name="a task", execution="main", session=session)
    task2 = FuncTask(lambda : None, name="a task", execution="main", session=session)
    assert session.tasks == {"a task": task2}

def test_existing_rename(session):
    session.config.task_pre_exist = 'rename'
    task1 = FuncTask(lambda : None, name="a task", execution="main", session=session)
    task2 = FuncTask(lambda : None, name="a task", execution="main", session=session)
    assert session.tasks == {task1, task2}
    assert task2.name == 'a task - 1'

    assert session['a task'] is task1
    assert session['a task - 1'] is task2
