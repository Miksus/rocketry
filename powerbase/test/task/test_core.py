from powerbase.core import Task


class DummyTask(Task):
    __register__ = False

    def execute_action(self, *args, **kwargs):
        return 


def test_delete(session):
    task = DummyTask(name="mytest")
    assert session.tasks == {"mytest": task}
    task.delete()
    assert session.tasks == {}