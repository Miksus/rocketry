from redengine.core import Task


class DummyTask(Task):
    __register__ = False

    def execute(self, *args, **kwargs):
        return 


def test_delete(session):
    task = DummyTask(name="mytest")
    assert session.tasks == {"mytest": task}
    task.delete()
    assert session.tasks == {}