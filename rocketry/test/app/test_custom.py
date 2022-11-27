import logging

from rocketry import Rocketry
from rocketry.args import Arg
from rocketry.conditions.task.task import TaskStarted
from rocketry.conds import condition, true
from rocketry.args import argument, Task

def set_logging_defaults():
    task_logger = logging.getLogger("rocketry.task")
    task_logger.handlers = []
    task_logger.setLevel(logging.WARNING)

def test_init_args_in_cond(session, tmpdir):
    set_logging_defaults()

    app = Rocketry(execution="main")

    @app.cond()
    def file_exists(file):
        if file == "exists.txt":
            return True
        if file == "non_existent.txt":
            return False
        raise

    # Creating some tasks
    @app.task(file_exists("exists.txt"))
    def do_always():
        ...

    @app.task(file_exists("non_existent.txt"))
    def do_never():
        ...

    app.session.config.shut_cond = TaskStarted(task=do_always)
    app.run()
    # Assert and test tasks
    assert app.session[do_always].status == "success"
    assert app.session[do_never].status is None

    assert app.session[do_always].logger.filter_by().count() >= 2
    assert app.session[do_never].logger.filter_by().count() == 0


def test_decors():
    set_logging_defaults()

    # Creating app
    app = Rocketry(config={'execution': 'main'})

    @argument()
    def myarg(task=Task()):
        assert task.name == "do_things"
        return "a value"

    @condition()
    def is_bar(arg=myarg):
        assert arg == "a value"
        return True

    @app.task(true & is_bar)
    def do_things(arg=myarg):
        assert arg == "a value"

    app.session.config.shut_cond = TaskStarted(task=do_things)
    app.run()

    logger = app.session['do_things'].logger
    assert logger.filter_by(action="success").count() == 1

def test_decors_pass_args():
    set_logging_defaults()

    # Creating app
    app = Rocketry(config={'execution': 'main'}, parameters={"session_arg": "arg val"})

    @argument()
    def myarg(arg=Arg("session_arg")):
        assert arg == "arg val"
        return "a value"

    @condition()
    def is_bar(passed_arg, arg=myarg):
        assert passed_arg == "cond arg val"
        assert arg == "a value"
        return True

    @app.task(true & is_bar(passed_arg="cond arg val"))
    def do_things(arg=myarg):
        assert arg == "a value"

    app.session.config.shut_cond = TaskStarted(task=do_things)
    app.run()

    logger = app.session['do_things'].logger
    assert logger.filter_by(action="success").count() == 1