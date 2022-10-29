from datetime import datetime, timedelta
from rocketry.conditions.scheduler import SchedulerCycles
from rocketry.conds import daily
from rocketry.events import Event, EventStream, event_stream
from rocketry.tasks import FuncTask

def test_event_none(session):

    event_calls = []

    @event_stream()
    def my_event():
        event_calls.append("called")
        return None

    assert my_event.model is Event 

    task1 = FuncTask(
        lambda: None, 
        start_cond=my_event,
        execution="main", 
        session=session,
        name="do_always 1"
    )

    session.config.shut_cond = SchedulerCycles() >= 3
    session.start()

    repo = session.get_repo()
    logs = [{"task_name": log.task_name, "action": log.action} for log in repo.filter_by()]
    assert logs == []

    # Check the event is checked once per cycle
    assert len(event_calls) == 3 # 3 checks. When getting param, event func not run

def test_event_as_datetime(session):

    event_calls = []

    @event_stream()
    def my_event():
        event_calls.append("called")
        return datetime(2022, 1, 1)

    def do_things(event=my_event):
        assert isinstance(event, datetime)

    assert my_event.model is Event 

    task1 = FuncTask(
        do_things, 
        start_cond=my_event,
        execution="main", 
        session=session,
        name="do_always 1"
    )
    task2 = FuncTask(
        do_things, 
        start_cond=my_event,
        execution="main", 
        session=session,
        name="do_always 2"
    )

    session.config.shut_cond = SchedulerCycles() >= 3
    session.start()

    repo = session.get_repo()
    logs = [{"task_name": log.task_name, "action": log.action} for log in repo.filter_by()]
    assert logs == [
        {"task_name": "do_always 1", "action": "run"},
        {"task_name": "do_always 1", "action": "success"},
        {"task_name": "do_always 2", "action": "run"},
        {"task_name": "do_always 2", "action": "success"},
    ]

    # Check the event is checked once per cycle
    assert len(event_calls) == 3 # 3 checks. When getting param, event func not run
    assert len(my_event.event_stack) == 1

def test_event_as_value(session):

    event_calls = []

    @event_stream()
    def my_event():
        event_calls.append("called")
        return "a value"

    def do_things(event=my_event):
        assert event == "a value"

    assert my_event.model is Event 

    task1 = FuncTask(
        do_things, 
        start_cond=my_event,
        execution="main", 
        session=session,
        name="do_always 1"
    )
    task2 = FuncTask(
        do_things, 
        start_cond=my_event,
        execution="main", 
        session=session,
        name="do_always 2"
    )

    session.config.shut_cond = SchedulerCycles() >= 3
    session.start()

    repo = session.get_repo()
    logs = [{"task_name": log.task_name, "action": log.action} for log in repo.filter_by()]
    assert logs == [
        {"task_name": "do_always 1", "action": "run"},
        {"task_name": "do_always 1", "action": "success"},
        {"task_name": "do_always 2", "action": "run"},
        {"task_name": "do_always 2", "action": "success"},

        {"task_name": "do_always 1", "action": "run"},
        {"task_name": "do_always 1", "action": "success"},
        {"task_name": "do_always 2", "action": "run"},
        {"task_name": "do_always 2", "action": "success"},

        {"task_name": "do_always 1", "action": "run"},
        {"task_name": "do_always 1", "action": "success"},
        {"task_name": "do_always 2", "action": "run"},
        {"task_name": "do_always 2", "action": "success"},
    ]

    # Check the event is checked once per cycle
    assert len(event_calls) == 3 # 3 checks. When getting param, event func not run
    assert len(my_event.event_stack) == 1

def test_event_as_event(session):

    event_calls = []

    @event_stream()
    def my_event():
        event_calls.append("called")
        return Event(timestamp=datetime(2022, 1, 1), value="a value")

    def do_things(event=my_event):
        assert event == "a value"

    assert my_event.model is Event 

    task1 = FuncTask(
        do_things, 
        start_cond=my_event,
        execution="main", 
        session=session,
        name="do_always 1"
    )
    task2 = FuncTask(
        do_things, 
        start_cond=my_event,
        execution="main", 
        session=session,
        name="do_always 2"
    )

    session.config.shut_cond = SchedulerCycles() >= 3
    session.start()

    repo = session.get_repo()
    logs = [{"task_name": log.task_name, "action": log.action} for log in repo.filter_by()]
    assert logs == [
        {"task_name": "do_always 1", "action": "run"},
        {"task_name": "do_always 1", "action": "success"},
        {"task_name": "do_always 2", "action": "run"},
        {"task_name": "do_always 2", "action": "success"},
    ]

    # Check the event is checked once per cycle
    assert len(event_calls) == 3 # 3 checks. When getting param, event func not run
    assert len(my_event.event_stack) == 1

def test_event_multi(session):

    event_calls = []

    @event_stream()
    def my_event():
        event_calls.append("called")
        yield datetime(2022, 1, 1)
        yield datetime(2022, 1, 2)

    def do_things(event=my_event):
        assert isinstance(event, datetime)

    assert my_event.model is Event 

    task1 = FuncTask(
        do_things, 
        start_cond=my_event,
        execution="main", 
        session=session,
        name="do_always 1"
    )
    task2 = FuncTask(
        do_things, 
        start_cond=my_event,
        execution="main", 
        session=session,
        name="do_always 2"
    )

    session.config.shut_cond = SchedulerCycles() >= 3
    session.start()

    repo = session.get_repo()
    logs = [{"task_name": log.task_name, "action": log.action} for log in repo.filter_by()]
    assert logs == [
        {"task_name": "do_always 1", "action": "run"},
        {"task_name": "do_always 1", "action": "success"},
        {"task_name": "do_always 2", "action": "run"},
        {"task_name": "do_always 2", "action": "success"},
    ]

    # Check the event is checked once per cycle
    assert len(event_calls) == 3 # 3 checks. When getting param, event func not run
    assert len(my_event.event_stack) == 1

def test_event_in_future(session):

    event_calls = []

    @event_stream()
    def my_event():
        event_calls.append("called")
        return datetime.now() + timedelta(hours=2)

    def do_things(event=my_event):
        assert isinstance(event, datetime)

    assert my_event.model is Event 

    task1 = FuncTask(
        do_things, 
        start_cond=my_event,
        execution="main", 
        session=session,
        name="do_always 1"
    )
    task2 = FuncTask(
        do_things, 
        start_cond=my_event,
        execution="main", 
        session=session,
        name="do_always 2"
    )

    session.config.shut_cond = SchedulerCycles() >= 3
    session.start()

    repo = session.get_repo()
    logs = [{"task_name": log.task_name, "action": log.action} for log in repo.filter_by()]
    assert logs == []

    # Check the event is checked once per cycle
    assert len(event_calls) == 3 # 3 checks. When getting param, event func not run
    assert len(my_event.event_stack) == 1


def test_event_in_future_multiple(session):

    event_calls = []
    now = datetime.now()

    @event_stream()
    def my_event():
        event_calls.append("called")
        yield now
        yield now + timedelta(hours=1)
        yield now + timedelta(hours=2)

    def do_things(event=my_event):
        assert isinstance(event, datetime)

    assert my_event.model is Event 

    task1 = FuncTask(
        do_things, 
        start_cond=my_event,
        execution="main", 
        session=session,
        name="do_always 1"
    )
    task2 = FuncTask(
        do_things, 
        start_cond=my_event,
        execution="main", 
        session=session,
        name="do_always 2"
    )

    session.config.shut_cond = SchedulerCycles() >= 3
    session.start()

    repo = session.get_repo()
    logs = [{"task_name": log.task_name, "action": log.action} for log in repo.filter_by()]
    assert logs == []

    # Check the event is checked once per cycle
    assert len(event_calls) == 3 # 3 checks. When getting param, event func not run
    assert my_event.event_stack == [
        Event(timestamp=now, value=now),
        Event(timestamp=now + timedelta(hours=1), value=now),
        Event(timestamp=now + timedelta(hours=2), value=now),
    ]