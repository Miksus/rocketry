

from redengine.core import Scheduler
from redengine.conditions import TaskStarted, AlwaysTrue

from redengine.tasks import PyScript

import pytest
import pandas as pd


@pytest.mark.parametrize("execution", ["main", "thread", "process"])
@pytest.mark.parametrize(
    "script_path,expected_outcome,exc_cls",
    [
        pytest.param(
            "scripts/succeeding_script.py", 
            "success",
            None,
            id="Success"),
        pytest.param(
            "scripts/failing_script.py", 
            "fail", 
            RuntimeError,
            id="Failure"),
    ],
)
def test_run(tmpdir, script_files, script_path, expected_outcome, exc_cls, execution, session):
    # RACE CONDITION: 2021-08-16 Success-thread has been observed failing rarely (assert 3 == len(success) --> len(success) = 4)
    with tmpdir.as_cwd() as old_dir:

        task = PyScript(
            script_path, 
            name="a task",
            start_cond=AlwaysTrue(),
            execution=execution
        )

        scheduler = Scheduler(
            shut_cond=TaskStarted(task="a task") >= 3
        )
        scheduler()

        history = pd.DataFrame(task.logger.get_records())
        
        if expected_outcome == "fail":
            failures = history[history["action"] == "fail"]
            assert 3 == len(failures)

            # Check it has correct traceback in message
            for tb in failures["exc_text"]:
                assert "Traceback (most recent call last):" in tb
                assert "RuntimeError: This task failed" in tb
        else:
            success = history[history["action"] == "success"]
            assert 3 == len(success)

