import asyncio
import logging
import pytest

from redbird.logging import RepoHandler
from redbird.repos import MemoryRepo, CSVFileRepo

from rocketry import Rocketry
from rocketry.conditions.task.task import TaskStarted
from rocketry.args import Return, Arg, FuncArg
from rocketry import Session
from rocketry.session import Config
from rocketry.tasks import CommandTask
from rocketry.tasks import FuncTask
from rocketry.conds import false, true

def set_logging_defaults():
    task_logger = logging.getLogger("rocketry.task")
    task_logger.handlers = []
    task_logger.setLevel(logging.WARNING)

def test_app_defaults(tmpdir):
    set_logging_defaults()

    app = Rocketry()
    assert app.session.config.execution == "async"

    assert not app.session.config.silence_cond_check
    assert not app.session.config.silence_task_logging
    assert not app.session.config.silence_task_prerun

    assert app.session.config.task_logger_basename == "rocketry.task"
    assert app.session.config.scheduler_logger_basename == "rocketry.scheduler"
    assert app.session.config.cycle_sleep == 0.1
    assert not app.session.config.multilaunch
    assert app.session.config.restarting == 'replace'
    assert not app.session.config.force_status_from_logs
    assert app.session.config.task_priority == 0
    assert app.session.config.task_pre_exist == "raise"

    # Test logging
    task_logger = logging.getLogger("rocketry.task")

    # Till Red Bird supports equal, we need to test the handler one obj at a time
    assert len(task_logger.handlers) == 1
    assert isinstance(task_logger.handlers[0], RepoHandler)
    assert isinstance(task_logger.handlers[0].repo, MemoryRepo)

    assert isinstance(app.session, Session)

    # Test setting SQL repo
    with tmpdir.as_cwd():
        app = Rocketry(logger_repo=CSVFileRepo(filename="myrepo.csv"))
    assert len(task_logger.handlers) == 2
    assert isinstance(task_logger.handlers[0], RepoHandler)
    assert isinstance(task_logger.handlers[0].repo, CSVFileRepo)

    assert isinstance(app.session, Session)

    app = Rocketry(execution="thread")
    assert app.session.config.execution == "thread"

def test_deprecated():
    set_logging_defaults()

    with pytest.warns(DeprecationWarning):
        app = Rocketry(config={'task_execution': 'main'})
    assert app.session.config.execution == "main"

    with pytest.warns(DeprecationWarning):
        assert app.session.config.task_execution == "main"

def test_app_settings():
    app = Rocketry()
    assert app.session.config.execution == "async"

    # Test recommended
    app = Rocketry(execution="main", task_priority=10)
    assert app.session.config.execution == "main"

    # Test with conf
    app = Rocketry(config=Config(execution="main", task_priority=10))
    assert app.session.config.execution == "main"

    # Test with conf dict
    app = Rocketry(config=dict(execution="main", task_priority=10))
    assert app.session.config.execution == "main"

def test_task_creation():
    set_logging_defaults()

    app = Rocketry(execution="main")

    # Creating some tasks
    @app.task()
    def do_never():
        ...

    @app.task('daily')
    def do_func():
        return 'return value'

    app.task('daily', name="do_command", command="echo 'hello world'")
    app.task('daily', name="do_script", path=__file__)
    app.task('daily', name="do_lambda", func=lambda : None)

    # Assert and test tasks
    assert len(app.session.tasks) == 5

    assert isinstance(app.session['do_func'], FuncTask)
    assert isinstance(app.session['do_command'], CommandTask)
    assert isinstance(app.session['do_script'], FuncTask)
    assert isinstance(app.session['do_lambda'], FuncTask)

    assert app.session['do_never'].start_cond == false

def test_nested_args():
    set_logging_defaults()

    # Creating app
    app = Rocketry(execution="main")

    @app.param('arg_1')
    def my_arg_1():
        return 'arg 1'

    @app.param('arg_2')
    def my_func_2(arg=Arg('arg_1')):
        assert arg == "arg 1"
        return 'arg 2'

    @app.param('arg_3')
    def my_func_3(arg_1=Arg('arg_1'), arg_2=Arg("arg_2")):
        assert arg_1 == "arg 1"
        assert arg_2 == "arg 2"
        return 'arg 3'

    # Creating a task to test this
    @app.task(true)
    def do_daily(arg=Arg('arg_3')):

        assert arg == "arg 3"

    app.session.config.shut_cond = TaskStarted(task='do_daily')
    app.run()
    logger = app.session['do_daily'].logger
    assert logger.filter_by(action="success").count() == 1

def test_nested_args_from_func_arg():
    set_logging_defaults()

    # Creating app
    app = Rocketry(execution="main")

    @app.param('arg_1')
    def my_arg_1():
        return 'arg 1'

    def my_func_2(arg=Arg('arg_1')):
        assert arg == "arg 1"
        return 'arg 2'

    def my_func_3(arg_1=Arg('arg_1'), arg_2=FuncArg(my_func_2)):
        assert arg_1 == "arg 1"
        assert arg_2 == "arg 2"
        return 'arg 3'

    # Creating a task to test this
    @app.task(true)
    def do_daily(arg=FuncArg(my_func_3)):
        assert arg == "arg 3"

    app.session.config.shut_cond = TaskStarted(task='do_daily')
    app.run()
    logger = app.session['do_daily'].logger
    assert logger.filter_by(action="success").count() == 1

def test_arg_ref():
    set_logging_defaults()

    # Creating app
    app = Rocketry(execution="main")

    @app.param('arg_1')
    def my_arg_1():
        return 'arg 1'

    @app.param('arg_2')
    def my_arg_2():
        return 'arg 2'

    # Creating a task to test this
    @app.task(true)
    def do_daily(arg_1=Arg(my_arg_1), arg_2=Arg(my_arg_2)):
        assert arg_1 == "arg 1"
        assert arg_2 == "arg 2"

    app.session.config.shut_cond = TaskStarted(task='do_daily')
    app.run()
    logger = app.session['do_daily'].logger
    assert logger.filter_by(action="success").count() == 1

def test_app_async():
    set_logging_defaults()

    app = Rocketry(execution="main")

    # Creating some tasks
    @app.task()
    def do_never():
        ...

    @app.task('daily')
    def do_func():
        return 'return value'

    app.session.config.shut_cond = TaskStarted(task='do_func')
    asyncio.run(app.serve())
    assert 1 == app.session[do_func].logger.filter_by(action="success").count()

def test_app_run():
    set_logging_defaults()

    # Creating app
    app = Rocketry(execution="main")
    app.params(my_arg='session value')

    # Creating some params and conditions
    @app.param('my_func_arg')
    def my_func():
        return 'func arg value'

    @app.cond('is foo')
    def is_foo(arg=Arg("my_func_arg")):
        assert arg == "func arg value"
        return True

    # Creating some tasks
    @app.task('daily & is foo')
    def do_daily():
        return 'return value'

    @app.task("after task 'do_daily'")
    def do_after(arg=Return('do_daily'), session_arg=Arg('my_arg'), func_arg=Arg('my_func_arg'), func_arg_2=FuncArg(lambda: 'my val')):
        assert arg == 'return value'
        assert session_arg == 'session value'
        assert func_arg == 'func arg value'
        assert func_arg_2 == 'my val'

    @app.task("true")
    def do_fail():
        raise

    @app.task("false", execution='process', name="never done", parameters={'arg_1': 'something'})
    def do_never(arg_1):
        raise

    app.session.config.shut_cond = TaskStarted(task='do_after')

    # Testing the app has all relevant things
    session = app.session
    assert 'is foo' in list(session._cond_parsers)
    assert set(task.name for task in session.tasks) == {'do_daily', 'do_after', 'do_fail', 'never done'}

    app.run()

    logger = app.session['do_after'].logger
    assert logger.filter_by(action="success").count() == 1

    logger = app.session['do_fail'].logger
    assert logger.filter_by(action="fail").count() == 1

    # Test the parameters are passed to a task
    task_example = session['never done']
    assert task_example.execution == 'process'
    assert task_example.name == 'never done'
    assert dict(task_example.parameters) == {'arg_1': 'something'}


def test_task_name():
    set_logging_defaults()

    app = Rocketry(execution="main")

    @app.task()
    def do_func():
        return 'return value'

    assert app.session[do_func].name == "do_func"

def test_delete_task():
    set_logging_defaults()

    app = Rocketry(execution="main")

    @app.task(name="task 1")
    def task_1():
        return 1

    @app.task()
    def task_2():
        return 1

    assert len(app.session.tasks) == 2

    app.session.remove_task("task 1")
    assert len(app.session.tasks) == 1

    app.session.remove_task(task_2)
    assert len(app.session.tasks) == 0
