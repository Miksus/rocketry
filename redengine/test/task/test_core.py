
from redengine.core import Task
from redengine.core.condition.base import AlwaysFalse, AlwaysTrue, BaseCondition

class DummyTask(Task):
    __register__ = False

    def execute(self, *args, **kwargs):
        return 

def test_defaults(session):
    task = DummyTask(name="mytest")
    assert task.name == "mytest"
    assert isinstance(task.start_cond, AlwaysFalse)
    assert isinstance(task.run_cond, AlwaysTrue)
    assert isinstance(task.end_cond, AlwaysFalse)

def test_delete(session):
    task = DummyTask(name="mytest")
    assert session.tasks == {"mytest": task}
    task.delete()
    assert session.tasks == {}