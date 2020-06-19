from pypipe.conditions import task_ran, task_failed, task_succeeded

from pypipe import Scheduler, FuncTask
from pypipe.task.base import Task

Task.use_instance_naming = True

def run_successful_func():
    print("Running func")

def run_failing_func():
    print("Running func")
    raise RuntimeError("Task failed")

def test_task_has_run(tmpdir):
    # Going to tempdir to dump the log files there

    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            run_successful_func, 
            execution="daily",
        )
        task()
        condition = task_ran(task=task)
        print(condition.function())
        assert bool(condition)

def test_task_has_not_run(tmpdir):
    # Going to tempdir to dump the log files there

    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            run_successful_func, 
            execution="daily",
        )

        condition = task_ran(task=task)
        assert not bool(condition)


def test_task_set(tmpdir):
    # Going to tempdir to dump the log files there

    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            run_successful_func, 
            start_cond=task_ran,
            execution="daily",
        )
        assert task.start_cond.kwargs["task"] is task
