from pypipe.builtin.conditions import (
    TaskStarted, 

    TaskFinished, 
    TaskFailed, 
    TaskSucceeded,

    DependFinish,
    DependFailure,
    DependSuccess
)
from pypipe.core.conditions import set_statement_defaults

from pypipe.core import Scheduler
from pypipe.builtin.task import FuncTask
from pypipe.core import reset

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