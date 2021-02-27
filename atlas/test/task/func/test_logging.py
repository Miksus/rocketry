import logging
import pytest
import multiprocessing
from queue import Empty

from atlas.core import Scheduler
from atlas.task import FuncTask
from atlas.core.task.base import Task, get_task
from atlas.log import CsvHandler
from atlas import session

import pandas as pd

def run_success():
    pass

def test_running(tmpdir):
    
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = FuncTask(
            lambda : None,
            execution="main"
        )
        task.log_running()
        assert "run" == task.status
        assert task.is_running

def test_success(tmpdir):
    
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = FuncTask(
            lambda : None,
            execution="main"
        )
        task.log_running()
        task.log_success()
        assert "success" == task.status
        assert not task.is_running

def test_fail(tmpdir):
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = FuncTask(
            lambda : None,
            execution="main"
        )
        task.log_running()
        task.log_failure()
        assert "fail" == task.status
        assert not task.is_running

def test_handle(tmpdir):

    def create_record(action, task_name):
        # Util func to create a LogRecord
        record = logging.LogRecord(
            level=logging.INFO,
            exc_info=None,
            # These should not matter:
            name="atlas.task._process",
            pathname=__file__,
            lineno=1,
            msg="",
            args=None,
        )
        record.action = action
        record.task_name = task_name
        return record

    # Tests Task.handle (used in process tasks)
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = FuncTask(
            lambda : None,
            execution="main",
            name="a task"
        )
        # Creating the run log
        record_run = create_record("run", task_name="a task")

        # Creating the outcome log
        record_finish = create_record("success", task_name="a task")
        
        task.log_record(record_run)
        assert "run" == task.status
        assert task.is_running

        task.log_record(record_finish)
        assert "success" == task.status
        assert not task.is_running

        df = session.get_task_log()
        records = df[["task_name", "action"]].to_dict(orient="records")
        assert [
            {"task_name": "a task", "action": "run"},
            {"task_name": "a task", "action": "success"},
        ] == records

def test_without_handlers(tmpdir):
    with tmpdir.as_cwd() as old_dir:

        logger = logging.getLogger("atlas.task.test")
        logger.handlers = []
        logger.propagate = False

        task = FuncTask(
            lambda : None, 
            name="task",
            start_cond="always true",
            logger="atlas.task.test",
            execution="main",
        )
        task()
        assert task.status is None


@pytest.mark.parametrize("method",
    [
        pytest.param("log_success", id="Success"),
        pytest.param("log_failure", id="Failure"),
        pytest.param("log_inaction", id="Inaction"),
        pytest.param("log_termination", id="Termination"),
    ],
)
def test_action_start(tmpdir, method):
    
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = FuncTask(
            lambda : None,
        )
        task.log_running()
        getattr(task, method)()

        df = session.get_task_log()

        # First should not have action_start
        assert pd.isna(df["action_start"].tolist()[0])

        # Second should and that should be datetime
        assert "nan" != str(df["action_start"].tolist()[1])
        assert "2000-01-01" <= str(df["action_start"].tolist()[1])


def test_process_no_double_logging(tmpdir):
    # 2021-02-27 there is a bug that Raspbian logs process task logs twice
    # while this is not occuring on Windows. This tests the bug.

    expected_actions = ["run", "success"]
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = FuncTask(
            run_success, 
            name="a task",
            execution="process"
        )

        
        log_queue = multiprocessing.Queue(-1)
        return_queue = multiprocessing.Queue(-1)

        # Start the process
        proc = multiprocessing.Process(target=task._run_as_process, args=(log_queue, return_queue, None), daemon=None) 
        proc.start()

        # Testing there is no log records yet in the log
        # (as the records should not been handled yet)
        df = session.get_task_log()
        assert [] == df["action"].tolist(), "Double logging. The log file is not empty before handling the records. Process bypasses the queue."
        
        # Do the logging manually (copied from the method)
        actual_actions = []
        while True:
            try:
                record = log_queue.get(block=True, timeout=2)
            except Empty:
                break
            else:
                task.log_record(record)
                actual_actions.append(record.action)

        # Tests
        n_run = actual_actions.count("run")
        n_success = actual_actions.count("success")

        # If fails here, logs not formed (not double logging)
        assert n_run > 0 and n_success > 0, "No log records created/sent by the child process."

        # If fails here, double logging caused by creating too many records
        assert (
            n_run == 1 and n_success == 1
        ), "Double logging. Caused by creating multiple records (Task.log_running & Task.log_success)."

        # If fails here, double logging caused by multiple handlers
        handlers = task.logger.logger.handlers
        handlers[0] # Checking it has atleast 2
        handlers[1] # Checking it has atleast 2
        assert (
            isinstance(handlers[0], logging.StreamHandler)
            and isinstance(handlers[1], CsvHandler)
            and len(handlers) == 2
        ), f"Double logging. Too many handlers: {handlers}"

        # If fails here, double logging caused by Task.log_record
        df = session.get_task_log()
        records = df[["task_name", "action"]].to_dict(orient="records")
        n_run = records.count({"task_name": "a task", "action": "run"})
        n_success = records.count({"task_name": "a task", "action": "run"})
        assert n_run > 0 and n_success > 0, "No log records formed to log."

        assert n_run == 1 and n_success == 1, "Double logging. Bug in Task.log_record probably."