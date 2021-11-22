
import pytest
from redengine.conditions import TaskCond
from redengine.conditions import SchedulerCycles, SchedulerStarted, TaskStarted, AlwaysFalse, AlwaysTrue
import re

from redengine.core import Scheduler
from redengine.tasks import FuncTask

def is_foo(place):
    print(f"evaluating: {place}")
    if place == "home":
        return True
    else:
        return False

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_taskcond(capsys, session, execution):
    # Check if one check is enough
    cond = TaskCond(syntax=re.compile(r"is foo at (?P<place>.+)"), start_cond="every 1 min", active_time="past 10 seconds", execution=execution)
    cond(is_foo)
    
    task = FuncTask(lambda: None, start_cond="is foo at home", name="a task", execution="main")
    task_not_running = FuncTask(lambda: None, start_cond="is foo at work", name="task not running", execution="main")

    # This condition should be cached (not creating third task)
    FuncTask(lambda: None, start_cond="is foo at work", name="task not running 2", execution="main")

    scheduler = Scheduler( # (TaskStarted(task="a task") >= 2) | 
        shut_cond=(TaskStarted(task="a task") >= 2) | ~SchedulerStarted(period="past 20 seconds")
    )

    scheduler()
    
    history = list(session.get_task_log())
    history_task = [
        {"task_name": rec['task_name'], "action": rec["action"]} 
        for rec in history
        if rec['task_name'] == "a task"
    ]
    assert history_task == [
        {"task_name": "a task", "action": "run"},
        {"task_name": "a task", "action": "success"},
        {"task_name": "a task", "action": "run"},
        {"task_name": "a task", "action": "success"},
    ]

    history_task = [
        {"task_name": rec['task_name'], "action": rec["action"]} 
        for rec in history
        if rec['task_name'] == "task not running"
    ]
    assert history_task == []

    cond_tasks = [task for task in session.tasks.values() if task.name.startswith("_condition")]
    assert len(cond_tasks) == 2
    for cond_task in cond_tasks:
        history_check = [
            {"task_name": rec['task_name'], "action": rec["action"]} 
            for rec in history
            if rec['task_name'] == cond_task.name
        ]
        assert history_check == [
            {"task_name": cond_task.name, "action": "run"},
            {"task_name": cond_task.name, "action": "success"},
        ] 