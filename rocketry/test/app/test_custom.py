
import asyncio
import logging

from rocketry import Rocketry
from rocketry.conditions.task.task import TaskStarted

def set_logging_defaults():
    task_logger = logging.getLogger("rocketry.task")
    task_logger.handlers = []
    task_logger.setLevel(logging.WARNING)

def test_init_args_in_cond(session, tmpdir):
    set_logging_defaults()

    app = Rocketry(config={'task_execution': 'main'})

    @app.cond()
    def file_exists(file):
        if file == "exists.txt":
            return True
        elif file == "non_existent.txt":
            return False
        else:
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