import logging
import pytest
import multiprocessing
from queue import Empty

from atlas.core import Scheduler
from atlas.task import FuncTask
from atlas.core.task.base import Task, get_task
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
        
        # Do the logging manually (copied from the method)
        actual_actions = []
        while True:
            try:
                record = log_queue.get(block=True, timeout=2)
            except Empty:
                break
            else:
                print("asd")
                task.log_record(record)
                actual_actions.append(record.action)

        # Tests
        assert expected_actions == actual_actions

        df = session.get_task_log()
        records = df[["task_name", "action"]].to_dict(orient="record")
        assert [
            {"task_name": "a task", "action": "run"},
            {"task_name": "a task", "action": "success"},
        ] == records