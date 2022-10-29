import asyncio
from datetime import datetime
from rocketry.conditions.api import new_scheduler_cycle
from rocketry.conditions.scheduler import SchedulerCycles
from rocketry.conds import true
from rocketry.events import batch_stream, Batch
from rocketry.log.log_record import RunRecord
from rocketry.tasks import FuncTask

def test_items_always(session):
    def get_run_id(task, params):
        return params['item']

    session.config.param_materialize = 'pre'
    session.config.func_run_id = get_run_id
    session.get_repo().model = RunRecord

    event_calls = []

    @batch_stream(true)
    def my_item():
        event_calls.append("called")
        n_calls = len(event_calls)
        if n_calls == 1:
            return "first"
        elif n_calls == 2:
            return "second"
        elif n_calls == 3:
            return "third"
        elif n_calls == 5:
            # Will be called 9 times: 3 cycles 
            return "5th"

    def do_things(item=my_item):
        assert isinstance(item, str)

    task1 = FuncTask(
        do_things, 
        start_cond=my_item,
        execution="main", 
        session=session,
        name="do_always 1"
    )
    task2 = FuncTask(
        do_things, 
        start_cond=my_item,
        execution="main", 
        session=session,
        name="do_always 2"
    )

    assert event_calls == []
    session.config.shut_cond = SchedulerCycles() >= 3
    session.start()

    repo = session.get_repo()
    logs = [{"task_name": log.task_name, "action": log.action, "param": log.run_id} for log in repo.filter_by()]
    assert logs == [
        {"task_name": "do_always 1", "action": "run", 'param': 'first'},
        {"task_name": "do_always 1", "action": "success", 'param': 'first'},
        
        {"task_name": "do_always 2", "action": "run", 'param': 'second'},
        {"task_name": "do_always 2", "action": "success", 'param': 'second'},

        {"task_name": "do_always 1", "action": "run", 'param': 'third'},
        {"task_name": "do_always 1", "action": "success", 'param': 'third'},

        {"task_name": "do_always 2", "action": "run", 'param': '5th'},
        {"task_name": "do_always 2", "action": "success", 'param': '5th'},
    ]

    # Check the event is checked once per cycle
    assert len(event_calls) == 10 # 3 checks: 3 cycles * 2 tasks + 4 arg calls

def test_batch(session):
    def get_run_id(task, params):
        return params['item']

    session.config.param_materialize = 'pre'
    session.config.func_run_id = get_run_id
    session.get_repo().model = RunRecord

    event_calls = []

    @batch_stream()
    def my_item():
        event_calls.append("called")
        n_calls = len(event_calls)
        if n_calls == 1:
            return "first"
        elif n_calls == 2:
            return "second"
        elif n_calls == 3:
            return "third"
        elif n_calls == 5:
            # Will be called 9 times: 3 cycles 
            return "5th"

    def do_things(item=my_item):
        assert isinstance(item, str)

    task1 = FuncTask(
        do_things, 
        start_cond=my_item,
        execution="main", 
        session=session,
        name="do_always 1"
    )
    task2 = FuncTask(
        do_things, 
        start_cond=my_item,
        execution="main", 
        session=session,
        name="do_always 2"
    )

    assert event_calls == []
    session.config.shut_cond = SchedulerCycles() >= 9
    session.start()

    repo = session.get_repo()
    logs = [{"task_name": log.task_name, "action": log.action, "param": log.run_id} for log in repo.filter_by()]
    assert logs == [
        {"task_name": "do_always 1", "action": "run", 'param': 'first'},
        {"task_name": "do_always 1", "action": "success", 'param': 'first'},
        
        {"task_name": "do_always 1", "action": "run", 'param': 'second'},
        {"task_name": "do_always 1", "action": "success", 'param': 'second'},

        {"task_name": "do_always 1", "action": "run", 'param': 'third'},
        {"task_name": "do_always 1", "action": "success", 'param': 'third'},

        {"task_name": "do_always 1", "action": "run", 'param': '5th'},
        {"task_name": "do_always 1", "action": "success", 'param': '5th'},
    ]

    # Check the event is checked once per cycle
    assert len(event_calls) == 9 # 3 checks: 3 cycles * 2 tasks + 4 arg calls

def test_batch_generator(session):
    def get_run_id(task, params):
        return params['item']

    session.config.param_materialize = 'pre'
    session.config.func_run_id = get_run_id
    session.get_repo().model = RunRecord
    session.config.task_execution = 'async'

    event_calls = []

    @batch_stream()
    def my_item():
        event_calls.append("called")
        n_calls = len(event_calls)
        if n_calls == 3:
            yield "2nd: first"
            yield "2nd: second"
            yield "2nd: third"

        if n_calls == 5:
            yield "4th: first"
            yield "4th: second"
            yield "4th: third"

    def do_things(item=my_item):
        assert isinstance(item, str)
        
    task1 = FuncTask(
        do_things, 
        start_cond=my_item,
        execution="main", 
        session=session,
        name="do_always 1"
    )
    task2 = FuncTask(
        do_things, 
        start_cond=my_item,
        execution="main", 
        session=session,
        name="do_always 2"
    )

    assert event_calls == []

    session.config.shut_cond = SchedulerCycles() >= 20
    session.start()

    repo = session.get_repo()
    logs = [{"task_name": log.task_name, "action": log.action, "param": log.run_id} for log in repo.filter_by()]
    assert logs == [
        {"task_name": "do_always 1", "action": "run", 'param': '2nd: first'},
        {"task_name": "do_always 1", "action": "success", 'param': '2nd: first'},

        {"task_name": "do_always 2", "action": "run", 'param': '2nd: second'},
        {"task_name": "do_always 2", "action": "success", 'param': '2nd: second'},

        {"task_name": "do_always 1", "action": "run", 'param': '2nd: third'},
        {"task_name": "do_always 1", "action": "success", 'param': '2nd: third'},


        {"task_name": "do_always 1", "action": "run", 'param': '4th: first'},
        {"task_name": "do_always 1", "action": "success", 'param': '4th: first'},

        {"task_name": "do_always 2", "action": "run", 'param': '4th: second'},
        {"task_name": "do_always 2", "action": "success", 'param': '4th: second'},

        {"task_name": "do_always 1", "action": "run", 'param': '4th: third'},
        {"task_name": "do_always 1", "action": "success", 'param': '4th: third'},
    ]

    # Check the event is checked once per cycle
    assert len(event_calls) == 20

