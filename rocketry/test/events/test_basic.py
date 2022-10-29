from datetime import datetime, timedelta

import pytest
from rocketry.conditions.scheduler import SchedulerCycles
from rocketry.conds import daily
from rocketry.events import Event, EventStream, event_stream, trigger_stream
from rocketry.log.log_record import RunRecord
from rocketry.tasks import FuncTask

def no_event():
    return None

def past_event():
    print("Called")
    return datetime(2022, 1, 1)

def future_event():
    return datetime.now() + timedelta(hours=2)

def new_value():
    return "a value"

def generate_event(cls, **kwargs):
    def new_event():
        return cls(**kwargs)
    return new_event


@pytest.mark.parametrize('type_,event_func,expected_logs', [
    # Event
    pytest.param(Event, no_event, [], id="None"),
    pytest.param(Event, past_event, [
        {"task_name": "task 1", "action": "run", "run_id": "2022-01-01 00:00:00"},
        {"task_name": "task 1", "action": "success", "run_id": "2022-01-01 00:00:00"},
        {"task_name": "task 2", "action": "run", "run_id": "2022-01-01 00:00:00"},
        {"task_name": "task 2", "action": "success", "run_id": "2022-01-01 00:00:00"},
    ], id="Event: as datetime"),
    pytest.param(Event, new_value, [
        {"task_name": "task 1", "action": "run", "run_id": "a value"},
        {"task_name": "task 1", "action": "success", "run_id": "a value"},
        {"task_name": "task 2", "action": "run", "run_id": "a value"},
        {"task_name": "task 2", "action": "success", "run_id": "a value"},

        {"task_name": "task 1", "action": "run", "run_id": "a value"},
        {"task_name": "task 1", "action": "success", "run_id": "a value"},
        {"task_name": "task 2", "action": "run", "run_id": "a value"},
        {"task_name": "task 2", "action": "success", "run_id": "a value"},

        {"task_name": "task 1", "action": "run", "run_id": "a value"},
        {"task_name": "task 1", "action": "success", "run_id": "a value"},
        {"task_name": "task 2", "action": "run", "run_id": "a value"},
        {"task_name": "task 2", "action": "success", "run_id": "a value"},
    ], id="Event: as value"),
    pytest.param(Event, generate_event(Event, timestamp=datetime(2022, 1, 1), value="a value"), [
        {"task_name": "task 1", "action": "run", "run_id": "a value"},
        {"task_name": "task 1", "action": "success", "run_id": "a value"},
        {"task_name": "task 2", "action": "run", "run_id": "a value"},
        {"task_name": "task 2", "action": "success", "run_id": "a value"},
    ], id="Event: as event"),
    pytest.param(Event, future_event, [], id="Event: in future"),
])
def test_event(session, type_, event_func, expected_logs):

    def get_run_id(task, params):
        return str(params['event'])

    session.config.param_materialize = 'pre'
    session.config.func_run_id = get_run_id
    session.get_repo().model = RunRecord

    my_event = EventStream(model=type_)
    my_event.decorate(event_func)

    assert my_event.model is type_ 

    def do_things(event=my_event):
        ...

    task1 = FuncTask(
        do_things, 
        start_cond=my_event,
        execution="main", 
        session=session,
        name="task 1"
    )

    task2 = FuncTask(
        do_things, 
        start_cond=my_event,
        execution="main", 
        session=session,
        name="task 2"
    )

    session.config.shut_cond = SchedulerCycles() >= 3
    session.start()

    repo = session.get_repo()
    fields = set(field for log in expected_logs for field in log.keys())
    logs = [
        {field: getattr(log, field) for field in fields} 
        for log in repo.filter_by()
    ]
    assert logs == expected_logs
