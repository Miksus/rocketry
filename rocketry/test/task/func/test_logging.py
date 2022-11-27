import datetime
import logging
from queue import Empty
import multiprocessing

import pytest

from redbird.logging import RepoHandler

from rocketry.log.log_record import  MinimalRecord
from rocketry.tasks import FuncTask
from rocketry.testing.log import create_task_record
from rocketry.conds import true

def run_success():
    pass

@pytest.mark.parametrize("optimized", [True, False])
@pytest.mark.parametrize("last_status", ["run", "success", "fail", "inaction", "terminate"])
def test_set_cached_in_init(session, optimized, last_status):
    session.config.force_status_from_logs = not optimized

    logger = logging.getLogger("rocketry.task")
    for handler in logger.handlers:
        if hasattr(handler, "repo"):
            repo = handler.repo

    times = {
        "run": 946677600.0,
        "success": 1656709200.0,
        "fail": 1656795600.0,
        "terminate": 1656882000.0,
        "inaction":1656968400.0,
    }


    # A log record that should not be used
    for action, created in times.items():
        repo.add(MinimalRecord(
            task_name="mytask",
            action=action,
            created=created
        ))
    # Add one extra (which should be used instead of what we did above)
    times[last_status] = 1752958800.0
    repo.add(MinimalRecord(
        task_name="mytask",
        action=last_status,
        created=1752958800.0
    ))

    # Creating the task
    task = FuncTask(
        lambda : None,
        execution="main",
        name="mytask",
        session=session
    )
    task.set_cached()
    for action, created in times.items():
        dt = datetime.datetime.fromtimestamp(created)
        last_action_value = getattr(task, f"last_{action}")
        assert last_action_value == dt
    if last_status == "run":
        # The task was running according to logs when the task was created
        # Therefore it is considered crashed
        assert task.status == "crash"
    else:
        assert task.status == last_status

def test_running(session):

    task = FuncTask(
        lambda : None,
        execution="main",
        session=session
    )
    task.log_running()
    assert "run" == task.status
    assert task.is_running

def test_success(tmpdir, session):

    task = FuncTask(
        lambda : None,
        execution="main",
        session=session
    )
    task.log_running()
    task.log_success()
    assert "success" == task.status
    assert not task.is_running

def test_fail(tmpdir, session):

    task = FuncTask(
        lambda : None,
        execution="main",
        session=session
    )
    task.log_running()
    task.log_failure()
    assert "fail" == task.status
    assert not task.is_running

def test_without_running(tmpdir, session):
    "An edge case if for mysterious reason the task did not log running. Logging should still not crash"

    task = FuncTask(
        lambda : None,
        execution="main",
        session=session
    )
    task.log_failure()
    assert "fail" == task.status
    assert not task.is_running

def test_handle(session):

    def create_record(action, task_name):
        # Util func to create a LogRecord
        record = create_task_record(
            task_name=task_name,
            action=action,
            exc_info=None,
            # These should not matter:
            name="rocketry.task._process",
        )
        return record

    task = FuncTask(
        lambda : None,
        execution="main",
        name="a task",
        session=session
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

    records = session.get_task_log()
    records = [
        record.dict(exclude={"created"})
        for record in records
    ]
    assert [
        {"task_name": "a task", "action": "run"},
        {"task_name": "a task", "action": "success"},
    ] == records

def test_without_handlers(session):
    session.config.force_status_from_logs = True
    session.config.task_logger_basename = 'hdlr_test.task'

    logger = logging.getLogger("hdlr_test.task")
    logger.handlers = []
    logger.propagate = False
    logger.setLevel(logging.INFO)

    with pytest.warns(UserWarning) as warns:
        task = FuncTask(
            lambda : None,
            name="task 1",
            start_cond="always true",
            #logger="rocketry.task.test",
            execution="main",
            session=session
        )

    # Test warnings

    #assert str(warns[0].message) == "Logger 'rocketry.task.test' for task 'task 1' does not have ability to be read. Past history of the task cannot be utilized."
    warn_messages = [str(w.message) for w in warns]
    assert warn_messages == [
        "Logger hdlr_test.task cannot be read. Logging is set to memory. To supress this warning, please set a handler that can be read (redbird.logging.RepoHandler)"
    ]

    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], RepoHandler)

def test_without_handlers_status_warnings(session):
    session.config.force_status_from_logs = True

    logger = logging.getLogger("rocketry.task")
    logger.handlers = []
    logger.propagate = False
    logger.setLevel(logging.INFO)

    with pytest.warns(UserWarning) as warns:
        task = FuncTask(
            lambda : None,
            name="task 1",
            start_cond="always true",
            logger_name="rocketry.task.test",
            execution="main",
            session=session
        )
    # Removing the handlers that were added
    session.config.shut_cond = true
    with pytest.warns(UserWarning) as warns:
        session.start()
    # Test warnings
    expected_warnings = [
        "Logger 'rocketry.task.test' for task 'task 1' does not have ability to be read. Past history of the task cannot be utilized.",
        "Task 'task 1' logger is not readable. Latest run unknown.",
        "Task 'task 1' logger is not readable. Latest success unknown.",
        "Task 'task 1' logger is not readable. Latest fail unknown.",
        "Task 'task 1' logger is not readable. Latest terminate unknown.",
        "Task 'task 1' logger is not readable. Latest inaction unknown.",
        "Task 'task 1' logger is not readable. Latest crash unknown.",
    ]
    actual_warnings = [str(warn.message) for warn in warns]
    assert expected_warnings == actual_warnings

    # Removing the handlers that were added
    # to test without handlers
    logger.handlers = []

    with pytest.warns(UserWarning) as warns:
        task()
    # Cannot know the task.status as there is no log about it
    assert task.status == 'success'
    with pytest.warns(UserWarning) as warns:
        assert task.get_status() is None

    assert list(str(w.message) for w in warns) == [
        "Logger 'rocketry.task.test' for task 'task 1' does not have ability to be read. Past history of the task cannot be utilized.",
        "Task 'task 1' logger is not readable. Status unknown."
    ]

    session.config.force_status_from_logs = False
    with pytest.warns(UserWarning) as warns:
        task = FuncTask(
            lambda : None,
            name="task 2",
            start_cond="always true",
            logger="rocketry.task.test",
            execution="main",
            session=session
        )
    assert list(str(w.message) for w in warns) == [
        'Logger rocketry.task cannot be read. Logging is set to memory. To supress this warning, please set a handler that can be read (redbird.logging.RepoHandler)'
    ]

    task()
    # Can know the task.status as stored in a variable
    assert task.status == "success"
    assert task.get_status() == "success"

@pytest.mark.parametrize("method",
    [
        pytest.param("log_success", id="Success"),
        pytest.param("log_failure", id="Failure"),
        pytest.param("log_inaction", id="Inaction"),
        pytest.param("log_termination", id="Termination"),
    ],
)
def test_action_start(tmpdir, method, session):

    task = FuncTask(
        lambda : None,
        execution="main",
        session=session
    )
    task.log_running()
    getattr(task, method)()

    records = list(map(lambda e: e.dict(), session.get_task_log()))
    assert len(records) == 2

    # First should not have "end"
    first = records[0]
    assert first['created'] >= datetime.datetime(2000, 1, 1).timestamp()

    # Second should and that should be datetime
    last = records[1]
    assert first['created'] <= last['created']
    assert last['created'] < datetime.datetime(2200, 1, 1).timestamp()

def test_process_no_double_logging(session):
    # 2021-02-27 there is a bug that Raspbian logs process task logs twice
    # while this is not occuring on Windows. This tests the bug.
    #!NOTE: This test requires there are two handlers in
    # rocketry.task logger (Memory and Stream in this order)
    from rocketry.core.task import TaskRun
    task_logger = logging.getLogger("rocketry.task")
    task_logger.addHandler(logging.StreamHandler())

    expected_actions = ["run", "success"]

    task = FuncTask(
        run_success,
        name="a task",
        execution="process",
        session=session
    )

    log_queue = multiprocessing.Queue(-1)

    # Start the process
    task_run = TaskRun(start=0, task=None)
    proc = multiprocessing.Process(target=task._run_as_process, args=(None, None, task_run, log_queue, session.config, []), daemon=None)
    task_run.task = proc
    proc.start()

    # Do the logging manually (copied from the method)
    actual_actions = []
    records = []
    while True:
        try:
            record = log_queue.get(block=True, timeout=3)
        except Empty:
            break
        else:
            records.append(record)
            # task.log_record(record)
            actual_actions.append(record.action)

    # If fails here, double logging caused by creating too many records
    # Obseved to fail rarely with py36 (c2f0368ffa56c5b8933f1afa2917f2be1555fb7a)
    assert len(records) >= 2 # Testing not too few records (else not double logging bug)
    assert (
        ["run", "success"] == [rec.action for rec in records]
    ), "Double logging. Caused by creating multiple records (Task.log_running & Task.log_success) to the queue."

    # Testing there is no log records yet in the log
    # (as the records should not been handled yet)
    recs = list(session.get_task_log())
    assert len(recs) == 0, "Double logging. The log file is not empty before handling the records. Process bypasses the queue."

    for record in records:
        task.log_record(record)

    # If fails here, double logging caused by multiple handlers
    handlers = task.logger.logger.handlers
    handlers[0] # Checking it has atleast 2
    handlers[1] # Checking it has atleast 2
    assert (
        isinstance(handlers[1], logging.StreamHandler)
        and isinstance(handlers[0], RepoHandler)
        and len(handlers) == 2
    ), f"Double logging. Too many handlers: {handlers}"

    # If fails here, double logging caused by Task.log_record
    n_run = len(list(session.get_task_log(task_name="a task", action="run")))
    n_success = len(list(session.get_task_log(task_name="a task", action="success")))

    assert n_run > 0 and n_success > 0, "No log records formed to log."

    assert n_run == 1 and n_success == 1, "Double logging. Bug in Task.log_record probably."
