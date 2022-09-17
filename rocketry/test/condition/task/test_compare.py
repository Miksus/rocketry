from rocketry.conditions import (
    TaskFinished, 
)
from rocketry.tasks import FuncTask

def run_task(fail=False):
    print("Running func")
    if fail:
        raise RuntimeError("Task failed")

def test_task_finish_compare(tmpdir, session):
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        equals = TaskFinished(task="runned task") == 2
        greater = TaskFinished(task="runned task") > 2
        less = TaskFinished(task="runned task") < 2

        task = FuncTask(
            run_task, 
            name="runned task",
            execution="main",
            session=session
        )

        # Has not yet ran
        assert not bool(equals.observe(session=session))
        assert not bool(greater.observe(session=session))
        assert bool(less.observe(session=session))

        task()
        task()

        assert bool(equals.observe(session=session))
        assert not bool(greater.observe(session=session))
        assert not bool(less.observe(session=session))

        task()
        assert not bool(equals.observe(session=session))
        assert bool(greater.observe(session=session))
        assert not bool(less.observe(session=session))