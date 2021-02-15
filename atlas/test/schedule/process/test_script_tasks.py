

from atlas.core import Scheduler
from atlas.conditions import SchedulerCycles, TaskFinished, TaskStarted, DependSuccess, AlwaysTrue

from atlas.task import PyScript
#from atlas.core.task.base import Task
#
#
#Task.use_instance_naming = True
from atlas import session
import pytest

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
def test_run(tmpdir, script_files, script_path, expected_outcome, exc_cls):
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = PyScript(
            script_path, 
            name="a task",
            start_cond=AlwaysTrue()
        )

        scheduler = Scheduler(
            [
                task,
            ], shut_condition=TaskStarted(task="a task") >= 3
        )
        scheduler()

        history = task.get_history()
        
        if expected_outcome == "fail":
            failures = history[history["action"] == "fail"]
            assert 3 == len(failures)

            # Check it has correct traceback in message
            for tb in failures["message"]:
                assert "Traceback (most recent call last):" in tb
                assert "RuntimeError: This task failed" in tb
        else:
            success = history[history["action"] == "success"]
            assert 3 == len(success)

