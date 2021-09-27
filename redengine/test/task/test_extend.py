
import pytest
from redengine.core.task import Task, CLS_TASKS

@pytest.fixture(autouse=True)
def setup():
    orig_tasks = CLS_TASKS.copy()
    yield
    for cls in CLS_TASKS.copy():
        if cls not in orig_tasks:
            CLS_TASKS.pop(cls)

def test_custom(setup):
    assert "TaskPytest" not in CLS_TASKS

    class TaskPytest(Task):
        pass
    assert "TaskPytest" in CLS_TASKS
    assert CLS_TASKS["TaskPytest"] is TaskPytest

def test_custom_base(setup):
    assert "TaskPytest" not in CLS_TASKS

    class TaskPytest(Task):
        __register__ = False
    assert "TaskPytest" not in CLS_TASKS