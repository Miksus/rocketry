
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

def test_crash(session):
    task = DummyTask(name="mytest", session=session)
    task.log_running()
    assert task.status == "run"
    assert task.last_crash is None
    task.delete()

    # Recreating and now should log crash
    task = DummyTask(name="mytest", session=session)
    assert task.status == "crash"
    assert task.last_crash

    logs = task.logger.filter_by().all()
    assert [
        {'action': 'run', 'task_name': 'mytest'},
        {'action': 'crash', 'task_name': 'mytest'}
    ] == [log.dict(exclude={'created'}) for log in logs]
