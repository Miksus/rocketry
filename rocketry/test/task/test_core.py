import datetime
import logging
import pickle
from textwrap import dedent
import pytest
from rocketry.args.builtin import Return
from rocketry.core import Task as BaseTask
from rocketry.core.condition.base import AlwaysFalse
from rocketry.args import Arg, Session, Task
from rocketry.exc import TaskLoggingError
from rocketry.log import MinimalRecord
from rocketry import Session as SessionClass
from rocketry.testing.log import create_task_record

class DummyTask(BaseTask):

    def execute(self, *args, **kwargs):
        return

def test_defaults(session):
    task = DummyTask(name="mytest", session=session)
    assert task.name == "mytest"
    assert isinstance(task.start_cond, AlwaysFalse)
    assert isinstance(task.end_cond, AlwaysFalse)

def test_defaults_no_session(session):
    with pytest.warns(UserWarning):
        task = DummyTask(name="mytest")
    assert task.session is not session
    assert isinstance(task.session, SessionClass)
    assert task.session.tasks == {task}

def test_set_timeout(session):
    task = DummyTask(timeout="1 hour 20 min", session=session, name="1")
    assert task.timeout == datetime.timedelta(hours=1, minutes=20)

    task = DummyTask(timeout=datetime.timedelta(hours=1, minutes=20), session=session, name="2")
    assert task.timeout == datetime.timedelta(hours=1, minutes=20)

    task = DummyTask(timeout=20, session=session, name="3")
    assert task.timeout == datetime.timedelta(seconds=20)

def test_delete(session):
    task = DummyTask(name="mytest", session=session)
    assert session.tasks == {task}
    task.delete()
    assert session.tasks == set()

def test_set_invalid_status(session):
    task = DummyTask(name="mytest", session=session)
    with pytest.raises(ValueError):
        task.status = "not valid"

def test_failed_logging(session):

    class MyHandler(logging.Handler):
        def emit(self, record):
            raise RuntimeError("Oops")

    logging.getLogger("rocketry.task").handlers.insert(0, MyHandler())
    task = DummyTask(name="mytest", session=session)
    for func in (task.log_crash, task.log_failure, task.log_success, task.log_inaction, task.log_termination):
        with pytest.raises(TaskLoggingError):
            func()

    record = create_task_record(created=1, task_name="mytest", action="run")

    with pytest.raises(TaskLoggingError):
        task.log_record(record) # Used by process logging

def test_pickle(session):
    task_1 = DummyTask(name="mytest", session=session)
    pkl_obj = pickle.dumps(task_1)
    task_2 = pickle.loads(pkl_obj)
    assert task_1.name == task_2.name

def test_crash(session):
    task = DummyTask(name="mytest", session=session)
    task.set_cached()
    task.log_running()
    assert task.status == "run"
    assert task.last_crash is None
    task.delete()

    # Recreating and now should log crash
    task = DummyTask(name="mytest", session=session)
    task.set_cached()
    assert task.status == "crash"
    assert task.last_crash

    logs = task.logger.filter_by().all()
    assert [
        {'action': 'run', 'task_name': 'mytest'},
        {'action': 'crash', 'task_name': 'mytest'}
    ] == [log.dict(exclude={'created'}) for log in logs]

def test_json(session):
    session.parameters['x'] = 5
    repo = session.get_repo()
    repo.add(MinimalRecord(task_name="mytest", action="run", created=1640988000))
    repo.add(MinimalRecord(task_name="mytest", action="success", created=1640988060))

    task = DummyTask(name="mytest", parameters={
        "arg_2": Arg("x"),
        "arg_2": Return("another"),
        "session": Session(),
        "task": Task(),
        "another_task": Task('another')
    }, session=session)
    task.set_cached()
    j = task.json(indent=4)

    dt_run = datetime.datetime.fromtimestamp(1640988000)
    dt_success = datetime.datetime.fromtimestamp(1640988060)

    assert j == dedent("""
    {
        "permanent": false,
        "fmt_log_message": "Task '{task}' status: '{action}'",
        "daemon": null,
        "batches": [],
        "name": "mytest",
        "description": null,
        "logger_name": "rocketry.task",
        "execution": null,
        "priority": 0,
        "disabled": false,
        "force_run": false,
        "force_termination": false,
        "status": "success",
        "timeout": null,
        "parameters": {
            "arg_2": "Return('another', default=NOTSET)",
            "session": "session",
            "task": "Task()",
            "another_task": "Task('another')"
        },
        "start_cond": "false",
        "end_cond": "false",
        "multilaunch": null,
        "on_startup": false,
        "on_shutdown": false,
        "func_run_id": null
    }
    """
    .replace("<RUN>", dt_run.strftime("%Y-%m-%dT%H:%M:%S"))
    .replace("<SUCCESS>", dt_success.strftime("%Y-%m-%dT%H:%M:%S"))
    )[1:-1]
