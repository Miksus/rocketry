
import datetime
import pickle
import pytest
from rocketry.core import Task
from rocketry.core.condition.base import AlwaysFalse, AlwaysTrue, BaseCondition

class DummyTask(Task):

    def execute(self, *args, **kwargs):
        return 

def test_defaults(session):
    task = DummyTask(name="mytest")
    assert task.name == "mytest"
    assert isinstance(task.start_cond, AlwaysFalse)
    assert isinstance(task.end_cond, AlwaysFalse)

def test_set_timeout(session):
    task = DummyTask(timeout="1 hour 20 min", session=session, name="1")
    assert task.timeout == datetime.timedelta(hours=1, minutes=20)

    task = DummyTask(timeout=datetime.timedelta(hours=1, minutes=20), session=session, name="2")
    assert task.timeout == datetime.timedelta(hours=1, minutes=20)

    task = DummyTask(timeout=20, session=session, name="3")
    assert task.timeout == datetime.timedelta(seconds=20)

def test_delete(session):
    task = DummyTask(name="mytest")
    assert session.tasks == {task}
    task.delete()
    assert session.tasks == set()

def test_set_invalid_status(session):
    task = DummyTask(name="mytest")
    with pytest.raises(ValueError):
        task.status = "not valid"

def test_pickle(session):
    task_1 = DummyTask(name="mytest")
    pkl_obj = pickle.dumps(task_1)
    task_2 = pickle.loads(pkl_obj)
    assert task_1.name == task_2.name