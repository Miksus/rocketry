import logging
import pytest

from redbird.logging import RepoHandler
from redbird.repos import MemoryRepo
from rocketry.core.time.base import TimeDelta

from rocketry.conditions.scheduler import SchedulerStarted
from rocketry.conditions import TaskStarted, AlwaysTrue
from rocketry.log.log_record import LogRecord
from rocketry.tasks import FuncTask

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
    with tmpdir.as_cwd():
        task_logger = logging.getLogger(session.config.task_logger_basename)
        task_logger.handlers = [
            RepoHandler(repo=MemoryRepo(model=LogRecord))
        ]
        task = FuncTask(
            func_name="main",
            path=script_path,
            name="a task",
            start_cond=AlwaysTrue(),
            execution=execution,
            session=session
        )

        session.config.shut_cond = (TaskStarted(task="a task") >= 3) | ~SchedulerStarted(period=TimeDelta("15 seconds"))
        session.start()

        if expected_outcome == "fail":
            failures = list(task.logger.filter_by(action="fail").all())
            assert 3 == len(failures)

            # Check it has correct traceback in message
            for fail in failures:
                tb = fail.exc_text
                assert "Traceback (most recent call last):" in tb
                assert "RuntimeError: This task failed" in tb
        else:
            success = list(task.logger.filter_by(action="success").all())
            assert 3 == len(success)
