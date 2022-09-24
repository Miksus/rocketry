from rocketry.args import Task
from rocketry.tasks import FuncTask

def test_run(tmpdir, session):
    task1 = FuncTask(
        lambda : None,
        name="example 1",
        execution="main",
        session=session,
    )

    task2 = FuncTask(
        lambda : None,
        name="example 2",
        execution="main",
        session=session,
    )
    session.run("example 2")
    assert task1.status is None
    assert task2.status == "success"
    assert not task1.disabled
    assert not task2.disabled

def test_run_obey_cond(session):
    task1 = FuncTask(
        lambda : None,
        name="example 1",
        execution="main",
        session=session,
    )

    task2 = FuncTask(
        lambda : None,
        name="example 2",
        execution="main",
        session=session,
    )
    session.run("example 2", obey_cond=True)
    assert task1.status is None
    assert task2.status is None # start cond is false
    assert not task1.disabled
    assert not task2.disabled

def test_run_execution(session):
    def run_task(task=Task()):
        # The execution has been temporarily set as "main"
        assert task.execution == "main"
        assert task.is_alive_as_main()
        assert not task.is_alive_as_process()
    task1 = FuncTask(
        lambda : None,
        name="example 1",
        execution="main",
        session=session,
    )

    task2 = FuncTask(
        run_task,
        name="example 2",
        execution="process",
        session=session,
    )
    # Should crash in pickling if ran with execution process
    session.run("example 2", execution="main")
    assert task1.status is None
    assert task2.status == "success"
