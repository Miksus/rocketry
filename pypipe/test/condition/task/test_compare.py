from pypipe.conditions import (
    TaskStarted, 

    TaskFinished, 
    TaskFailed, 
    TaskSucceeded,

    DependFinish,
    DependFailure,
    DependSuccess,
    set_statement_defaults
)

from pypipe import Scheduler, FuncTask
from pypipe.task.base import Task
from pypipe import reset

import pytest
def run_task(fail=False):
    print("Running func")
    if fail:
        raise RuntimeError("Task failed")

def test_task_finish_compare(tmpdir):
    # Going to tempdir to dump the log files there
    reset()
    with tmpdir.as_cwd() as old_dir:
        equals = TaskFinished(task="runned task") == 2
        greater = TaskFinished(task="runned task") > 2
        less = TaskFinished(task="runned task") < 2

        task = FuncTask(
            run_task, 
            name="runned task"
        )

        # Has not yet ran
        assert not bool(equals)
        assert not bool(greater)
        assert bool(less)

        task()
        task()

        assert bool(equals)
        assert not bool(greater)
        assert not bool(less)

        task()
        assert not bool(equals)
        assert bool(greater)
        assert not bool(less)