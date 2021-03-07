
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