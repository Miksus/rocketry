
import pytest
from redengine.core.task import Task


def test_custom(session):
    assert "TaskPytest" not in session.cls_tasks

    class TaskPytest(Task):
        pass
    assert "TaskPytest" in session.cls_tasks
    assert session.cls_tasks["TaskPytest"] is TaskPytest

def test_custom_base(session):
    assert "TaskPytest" not in session.cls_tasks

    class TaskPytest(Task):
        __register__ = False
    assert "TaskPytest" not in session.cls_tasks