

from powerbase import Session
from powerbase.task import FuncTask, PyScript
from powerbase.core import Parameters, Scheduler, BaseCondition, Task
from powerbase.conditions import Any, All, AlwaysTrue, AlwaysFalse, Not

def test_get_task(tmpdir, session):
    with tmpdir.as_cwd() as old_dir:

        task = FuncTask(
            lambda : None, 
            name="example"
        )
        
        # By string
        t = session.get_task(task.name)
        assert t is task

        # By task (returns itself)
        t = session.get_task(task)
        assert t is task

def test_session_condition_defaults():
    "Test user made condition classes are registered correctly"
    session = Session()
    session.set_as_default()

    should_include = {
        "Any": Any,
        "All": All,
        "AlwaysTrue": AlwaysTrue,
        "AlwaysFalse": AlwaysFalse,
        "Not": Not,
    }
    assert should_include.items() <= Session.cond_cls.items()

    # Creating new condition class that should be automatically 
    # included to list of default cond_cls
    class MyCond(BaseCondition):
        pass
    assert "MyCond" not in Session.cond_cls
    assert session.cond_cls["MyCond"] is MyCond

def test_session_task_defaults():
    "Test user made task classes are registered correctly"
    session = Session()
    session.set_as_default()

    should_include = {
        "FuncTask": FuncTask,
        "PyScript": PyScript,
    }
    assert should_include.items() <= Session.task_cls.items()
    
    # Creating new task class that should be automatically 
    # included to list of default task_cls
    class MyTask(Task):
        pass
    assert "MyTask" not in Session.task_cls
    assert session.task_cls["MyTask"] is MyTask


def test_tasks_attr(tmpdir, session):
    with tmpdir.as_cwd() as old_dir:

        task1 = FuncTask(
            lambda : None, 
            name="example 1"
        )
        task2 = FuncTask(
            lambda : None, 
            name="example 2"
        )
        
        assert {"example 1": task1, "example 2": task2} == session.tasks

def test_clear(tmpdir, session):
    with tmpdir.as_cwd() as old_dir:

        assert {} == session.tasks
        assert Parameters() == session.parameters
        assert session.scheduler is None

        task1 = FuncTask(
            lambda : None, 
            name="example 1"
        )
        task2 = FuncTask(
            lambda : None, 
            name="example 2"
        )
        session.parameters["x"] = 1
        sched = Scheduler()
        
        assert Parameters(x=1) == session.parameters
        assert {"example 1": task1, "example 2": task2} == session.tasks
        assert session.scheduler is sched

        session.clear()

        assert {} == session.tasks
        assert Parameters() == session.parameters
        assert session.scheduler is None
