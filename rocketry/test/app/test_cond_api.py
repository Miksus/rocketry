
import logging

from rocketry import Rocketry
from rocketry.conditions import TaskStarted
from rocketry.conditions.api import after_success

from rocketry.conds import (
    false,
    daily, time_of_hour,
    after_fail, after_success, after_finish
)

def set_logging_defaults():
    task_logger = logging.getLogger("rocketry.task")
    task_logger.handlers = []
    task_logger.setLevel(logging.WARNING)

def test_app_run():
    set_logging_defaults()

    # Creating app
    app = Rocketry(config={'task_execution': 'main'})

    # Creating some tasks
    @app.task(false)
    def do_never():
        ...

    @app.task(daily)
    def do_daily():
        ...
    
    @app.task(after_success(do_daily))
    def do_after():
        ...

    @app.task(daily & (after_fail(do_never) | time_of_hour.before("10:00") | after_success("do_daily")))
    def do_daily_complex():
        ...

    app.session.config.shut_cond = TaskStarted(task='do_after')
    app.run()

    logger = app.session['do_after'].logger
    assert logger.filter_by(action="success").count() == 1
