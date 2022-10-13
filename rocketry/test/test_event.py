from datetime import datetime
from rocketry.conditions.scheduler import SchedulerCycles
from rocketry.conditions.task.task import TaskStarted
from rocketry.events import EventStream, event
from rocketry.tasks import FuncTask

def test_event_call_once(session):

    event_calls = []

    @event()
    def my_event():
        event_calls.append("called")
        return datetime.now()

    def do_things(event=my_event):
        assert isinstance(event, datetime)

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