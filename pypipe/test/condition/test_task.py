from pypipe.event import task_ran, task_failed, task_succeeded
from pypipe.conditions import HasOccurred
from pypipe import Task

def run_successful_func():
    print("Running func")

def run_failing_func():
    print("Running func")
    raise RuntimeError("Task failed")

def test_task_has_run(tmpdir):
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = Task(
            run_successful_func, 
            execution="daily",
        )
        task()
        condition = task_ran(task=task)
    assert bool(condition)

def test_task_has_not_run(tmpdir):
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = Task(
            run_successful_func, 
            execution="daily",
        )

        condition = task_ran(task=task)
    assert not bool(condition)


def test_task_set(tmpdir):
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = Task(
            run_successful_func, 
            start_cond=HasOccurred(task_ran),
            execution="daily",
        )
    assert task.start_cond.task is task

def test_task_set(tmpdir):
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = Task(
            run_successful_func, 
            start_cond=task_ran.times(3),
            execution="daily"
        )
        task = Task(
            run_successful_func, 
            start_cond=task_ran.at_least(3).past("2h"),
            execution="daily"
        )
    assert task.start_cond.task is task