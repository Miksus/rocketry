
from itertools import chain
import datetime
import logging
from typing import Optional
from pydantic import root_validator, validator

import pytest

from redbird.oper import in_, between
from redbird.logging import RepoHandler
from redbird.repos import MemoryRepo
from rocketry.conditions import TaskFinished
from rocketry.conditions.scheduler import SchedulerCycles

from rocketry.log.log_record import MinimalRecord
from rocketry.pybox.time.convert import to_datetime
from rocketry.tasks import FuncTask
from rocketry.exc import TaskLoggingError

def create_line_to_startup_file():
    with open("start.txt", "w", encoding="utf-8") as file:
        file.write("line created\n")

def create_line_to_shutdown():
    with open("shut.txt", "w", encoding="utf-8") as file:
        file.write("line created\n")

def do_success():
    ...

def do_fail():
    raise RuntimeError("Oops")

class CustomRecord(MinimalRecord):
    timestamp: Optional[datetime.datetime]
    start: Optional[datetime.datetime]
    end: Optional[datetime.datetime]
    runtime: Optional[datetime.timedelta]
    message: str

    @validator("start", pre=True)
    def parse_start(cls, value):
        if value is not None:
            return datetime.datetime.fromtimestamp(value)

    @validator("end", pre=True)
    def parse_end(cls, value):
        if value is not None:
            return datetime.datetime.fromtimestamp(value)

    @root_validator
    def validate_timestamp(cls, values):
        values['timestamp'] = datetime.datetime.fromtimestamp(values['created'])
        return values

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
@pytest.mark.parametrize("status", ["success", "fail"])
@pytest.mark.parametrize("on", ["startup", "normal", "shutdown"])
def test_failed_logging_run(execution, status, on, session):
    class MyHandler(logging.Handler):
        def emit(self, record):
            raise RuntimeError("Oops")
    logger = logging.getLogger("rocketry.task")
    logger.handlers.insert(0, MyHandler())
    task = FuncTask({"success": do_success, "fail": do_fail}[status], name="a task", execution=execution, session=session)
    task.run()

    if on == "startup":
        task.on_startup = True
    elif on == "shutdown":
        task.on_shutdown = True

    session.config.shut_cond = SchedulerCycles() >= 1
    with pytest.raises(TaskLoggingError):
        session.start()
    assert task.status == "fail"
    session.config.silence_task_logging = True

    # TODO: Perhaps CI gets stuck here
    #session.start()

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
@pytest.mark.parametrize("status", ["success", "fail"])
@pytest.mark.parametrize("on", ["startup", "normal", "shutdown"])
def test_failed_logging_finish(execution, status, on, session):
    class MyHandler(logging.Handler):
        def emit(self, record):
            if record.action != "run":
                raise RuntimeError("Oops")

    if on == "normal":
        session.config.shut_cond = TaskFinished(task="a task") >= 1
    else:
        session.config.shut_cond = SchedulerCycles() == 1

    logger = logging.getLogger("rocketry.task")
    logger.handlers.insert(0, MyHandler())
    task = FuncTask({"success": do_success, "fail": do_fail}[status], name="a task", execution=execution, session=session)
    task.run()
    if on == "startup":
        task.on_startup = True
    elif on == "shutdown":
        task.on_shutdown = True
    with pytest.raises(TaskLoggingError):
        session.start()
    assert task.status == "fail"

    session.remove_task(task)

    task = FuncTask({"success": do_success, "fail": do_fail}[status], name="b task", execution=execution, session=session)
    task.run()

    session.config.silence_task_logging = True
    session.run(task)

    assert task.status == "fail"

@pytest.mark.parametrize("on", ["startup", "normal", "shutdown"])
def test_failed_set_cache(on, session):
    class MyHandler(logging.Handler):
        def emit(self, record):
            if record.action != "run":
                raise RuntimeError("Oops")

    if on == "normal":
        session.config.shut_cond = TaskFinished(task="a task") >= 1
    else:
        session.config.shut_cond = SchedulerCycles() == 1

    logger = logging.getLogger("rocketry.task")
    logger.handlers.insert(0, MyHandler())
    task = FuncTask(do_success, name="a task", session=session)
    task.log_running()
    if on == "startup":
        task.on_startup = True
    elif on == "shutdown":
        task.on_shutdown = True
    with pytest.raises(TaskLoggingError):
        session.start()
    assert task.status == "fail"

    session.remove_task(task)
    task = FuncTask(do_success, name="a task", session=session)
    task.log_running()
    session.config.silence_task_logging = True
    session.start()
    assert task.status == "fail"

@pytest.mark.parametrize(
    "query,expected",
    [
        pytest.param(
            {"action": "run"},
            [
                {'task_name': 'task1', 'timestamp': datetime.datetime(2021, 1, 1, 0, 0, 0), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 0, 0, 0), 'message': "Task 'task1' status: 'run'"},
                {'task_name': 'task2', 'timestamp': datetime.datetime(2021, 1, 1, 1, 0, 0), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 1, 0, 0), 'message': "Task 'task2' status: 'run'"},
                {'task_name': 'task3', 'timestamp': datetime.datetime(2021, 1, 1, 2, 0, 0), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 2, 0, 0), 'message': "Task 'task3' status: 'run'"},
                {'task_name': 'task4', 'timestamp': datetime.datetime(2021, 1, 1, 3, 0, 0), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 3, 0, 0), 'message': "Task 'task4' status: 'run'"},
            ],
            id="Get running"),
        pytest.param(
            {"action": in_(["success", "fail"])},
            [
                {'task_name': 'task1', 'created': datetime.datetime(2021, 1, 1, 4, 0, 0).timestamp(), 'action': 'success', 'start': datetime.datetime(2021, 1, 1, 0, 0, 0), 'end': datetime.datetime(2021, 1, 1, 4, 0, 0), 'runtime': datetime.timedelta(hours=4), 'message': "Task 'task1' status: 'success'"},
                {'task_name': 'task2', 'created': datetime.datetime(2021, 1, 1, 5, 0, 0).timestamp(), 'action': 'fail',    'start': datetime.datetime(2021, 1, 1, 1, 0, 0), 'end': datetime.datetime(2021, 1, 1, 5, 0, 0), 'runtime': datetime.timedelta(hours=4), 'message': "Task 'task2' status: 'fail'"},
            ],
            id="get succees & failure"),
        pytest.param(
            {"timestamp": between(to_datetime("2021-01-01 02:00:00"), to_datetime("2021-01-01 03:00:00"))},
            [
                {'task_name': 'task3', 'created': datetime.datetime(2021, 1, 1, 2, 0, 0).timestamp(), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 2, 0, 0), 'message': "Task 'task3' status: 'run'"},
                {'task_name': 'task4', 'created': datetime.datetime(2021, 1, 1, 3, 0, 0).timestamp(), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 3, 0, 0), 'message': "Task 'task4' status: 'run'"},
            ],
            id="get time span (datetime)"),
        pytest.param(
            {"timestamp": between(None, to_datetime("2021-01-01 03:00:00"), none_as_open=True), "action": "run"},
            [
                {'task_name': 'task1', 'created': datetime.datetime(2021, 1, 1, 0, 0, 0).timestamp(), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 0, 0, 0), 'message': "Task 'task1' status: 'run'"},
                {'task_name': 'task2', 'created': datetime.datetime(2021, 1, 1, 1, 0, 0).timestamp(), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 1, 0, 0), 'message': "Task 'task2' status: 'run'"},
                {'task_name': 'task3', 'created': datetime.datetime(2021, 1, 1, 2, 0, 0).timestamp(), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 2, 0, 0), 'message': "Task 'task3' status: 'run'"},
                {'task_name': 'task4', 'created': datetime.datetime(2021, 1, 1, 3, 0, 0).timestamp(), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 3, 0, 0), 'message': "Task 'task4' status: 'run'"},
            ],
            id="get time span (datetime, open left)"),
        pytest.param(
            {"timestamp": between(to_datetime("2021-01-01 02:00:00"), None, none_as_open=True), "action": "run"},
            [
                {'task_name': 'task3', 'created': datetime.datetime(2021, 1, 1, 2, 0, 0).timestamp(), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 2, 0, 0), 'message': "Task 'task3' status: 'run'"},
                {'task_name': 'task4', 'created': datetime.datetime(2021, 1, 1, 3, 0, 0).timestamp(), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 3, 0, 0), 'message': "Task 'task4' status: 'run'"},
            ],
            id="get time span (datetime, open right)"),
        pytest.param(
            {"timestamp": between(None, None, none_as_open=True), "action": "run"},
            [
                {'task_name': 'task1', 'created': datetime.datetime(2021, 1, 1, 0, 0, 0).timestamp(), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 0, 0, 0), 'message': "Task 'task1' status: 'run'"},
                {'task_name': 'task2', 'created': datetime.datetime(2021, 1, 1, 1, 0, 0).timestamp(), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 1, 0, 0), 'message': "Task 'task2' status: 'run'"},
                {'task_name': 'task3', 'created': datetime.datetime(2021, 1, 1, 2, 0, 0).timestamp(), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 2, 0, 0), 'message': "Task 'task3' status: 'run'"},
                {'task_name': 'task4', 'created': datetime.datetime(2021, 1, 1, 3, 0, 0).timestamp(), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 3, 0, 0), 'message': "Task 'task4' status: 'run'"},
            ],
            id="get time span (open left, open right)"),
        pytest.param(
            {"timestamp": between(datetime.datetime(2021, 1, 1, 2, 0, 0), datetime.datetime(2021, 1, 1, 3, 0, 0))},
            [
                {'task_name': 'task3', 'created': datetime.datetime(2021, 1, 1, 2, 0, 0).timestamp(), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 2, 0, 0), 'message': "Task 'task3' status: 'run'"},
                {'task_name': 'task4', 'created': datetime.datetime(2021, 1, 1, 3, 0, 0).timestamp(), 'action': 'run', 'start': datetime.datetime(2021, 1, 1, 3, 0, 0), 'message': "Task 'task4' status: 'run'"},
            ],
            marks=pytest.mark.xfail(reason="timerange passed as datetime but datetime is mocked and isinstance fails"),
            id="get time span (datetime)"),
    ],
)
def test_get_logs_params(tmpdir, mock_pydatetime, mock_time, query, expected, session):
    with tmpdir.as_cwd():
        task_logger = logging.getLogger(session.config.task_logger_basename)
        task_logger.handlers = [
            RepoHandler(repo=MemoryRepo(model=CustomRecord))
        ]

        task1 = FuncTask(lambda: None, name="task1", execution="main", session=session)
        task2 = FuncTask(lambda: None, name="task2", execution="main", session=session)
        task3 = FuncTask(lambda: None, name="task3", execution="main", session=session)
        task4 = FuncTask(lambda: None, name="task4", execution="main", session=session)

        task1.run()
        task2.run()
        task3.run()
        task4.run()

        # Start
        mock_pydatetime("2021-01-01 00:00:00")
        task1.log_running()

        mock_pydatetime("2021-01-01 01:00:00")
        task2.log_running()

        mock_pydatetime("2021-01-01 02:00:00")
        task3.log_running()

        mock_pydatetime("2021-01-01 03:00:00")
        task4.log_running()

        # Action
        mock_pydatetime("2021-01-01 04:00:00")
        task1.log_success()

        mock_pydatetime("2021-01-01 05:00:00")
        task2.log_failure()

        mock_pydatetime("2021-01-01 06:00:00")
        task3.log_inaction()

        mock_pydatetime("2021-01-01 07:00:00")
        task4.log_termination()

        #scheduler()

        logs = session.get_task_log(**query)
        assert isinstance(logs, chain)

        logs = list(logs)
        assert len(expected) == len(logs)
        logs = list(map(lambda e: e.dict(), logs))
        for e, a in zip(expected, logs):
            #assert e.keys() <= a.keys()
            # Check all expected items in actual (actual can contain extra)
            for key, val in e.items():
                assert a[key] == e[key]
            # assert e.items() <= a.items()
