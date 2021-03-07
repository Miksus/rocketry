
from atlas import session
from atlas.task import FuncTask
from atlas.core import Parameters, Scheduler

def test_get_task(tmpdir):
    with tmpdir.as_cwd() as old_dir:
        session.reset()
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

def test_tasks_attr(tmpdir):
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task1 = FuncTask(
            lambda : None, 
            name="example 1"
        )
        task2 = FuncTask(
            lambda : None, 
            name="example 2"
        )
        
        assert {"example 1": task1, "example 2": task2} == session.tasks

def test_clear(tmpdir):
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        assert {} == session.tasks
        assert Parameters() == session.parameters
        assert session.scheduler is None

        session.reset()
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
