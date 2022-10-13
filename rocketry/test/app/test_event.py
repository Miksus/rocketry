import datetime
import logging

from rocketry import Rocketry
from rocketry.conditions import TaskStarted
from rocketry.args import Arg
from rocketry.events import Event

def set_logging_defaults():
    task_logger = logging.getLogger("rocketry.task")
    task_logger.handlers = []
    task_logger.setLevel(logging.WARNING)

def test_event_notification(session):
    set_logging_defaults()

    app = Rocketry(config={'task_execution': 'main'})

    @app.event()
    def new_time():
        return datetime.datetime.now()

    @app.event()
    def old_time():
        return datetime.datetime(2022, 10, 11)

    @app.event()
    def never_time():
        return 

    # Creating some tasks
    @app.task(new_time)
    def do_always(event_date=new_time):
        ...

    @app.task(old_time)
    def do_once(event_date=old_time):
        assert event_date == datetime.datetime(2022, 10, 11)

    @app.task(never_time)
    def do_never(event_date=never_time):
        ...

    app.session.config.shut_cond = TaskStarted(task=do_always) >= 3
    app.run()

    s = app.session

    repo = s.get_repo()
    logs = [{"task_name": log.task_name, "action": log.action} for log in repo.filter_by()]
    assert logs == [
        {"task_name": "do_always", "action": "run"},
        {"task_name": "do_always", "action": "success"},
        {"task_name": "do_once", "action": "run"},
        {"task_name": "do_once", "action": "success"},
        {"task_name": "do_always", "action": "run"},
        {"task_name": "do_always", "action": "success"},
        {"task_name": "do_always", "action": "run"},
        {"task_name": "do_always", "action": "success"},
    ]


def test_event_carried_state_transfer(session):
    set_logging_defaults()

    app = Rocketry(config={'task_execution': 'main'})

    @app.event()
    def new_event_data():
        return {'name': 'Jack', 'age': 50}

    @app.event()
    def new_event():
        return Event(
            datetime=datetime.datetime(2022, 10, 11), 
            value={'name': 'Jack', 'age': 50}
        )

    # Creating some tasks
    @app.task(new_event_data)
    def do_always(my_event=new_event_data):
        assert my_event == {'name': 'Jack', 'age': 50}

    @app.task(new_event)
    def do_once(my_event=new_event):
        assert my_event == {'name': 'Jack', 'age': 50}

    app.session.config.shut_cond = TaskStarted(task=do_always) >= 3
    app.run()

    s = app.session

    repo = s.get_repo()
    logs = [{"task_name": log.task_name, "action": log.action} for log in repo.filter_by()]
    assert logs == [
        {"task_name": "do_always", "action": "run"},
        {"task_name": "do_always", "action": "success"},
        {"task_name": "do_once", "action": "run"},
        {"task_name": "do_once", "action": "success"},
        {"task_name": "do_always", "action": "run"},
        {"task_name": "do_always", "action": "success"},
        {"task_name": "do_always", "action": "run"},
        {"task_name": "do_always", "action": "success"},
    ]