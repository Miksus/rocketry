from pypipe.event import task_ran, task_failed, task_succeeded
from pypipe import Task

def run_successful_func():
    print("Running func")

def run_failing_func():
    print("Running func")
    raise RuntimeError("Task failed")


def test_task_not_run(tmpdir):
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = Task(
            run_successful_func, 
            execution="daily",
        )

        condition = task_ran(task=task)
    assert not bool(condition)