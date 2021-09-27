
import pytest
import pandas as pd

from redengine.core import Scheduler
from redengine.tasks import FuncTask
from redengine.conditions import TaskStarted, AlwaysTrue

def run_failing():
    raise RuntimeError("Task failed")

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_task_fail_traceback(tmpdir, execution, session):
    # There is a speciality in tracebacks in multiprocessing
    # See: https://bugs.python.org/issue34334

    # TODO: Delete. This has been handled now in test_core.py
    with tmpdir.as_cwd() as old_dir:

        task = FuncTask(run_failing, name="task", start_cond=AlwaysTrue(), execution=execution)

        scheduler = Scheduler(
            shut_cond=TaskStarted(task="task") >= 3
        )
        scheduler()
        history = pd.DataFrame(task.logger.get_records())
        failures = history[history["action"] == "fail"]
        assert 3 == len(failures)

        for tb in failures["exc_text"]:
            assert "Traceback (most recent call last):" in tb
            assert "RuntimeError: Task failed" in tb
