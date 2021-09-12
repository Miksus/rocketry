
from redengine.tasks import CommandTask
import pytest

def test_construct():
    task = CommandTask("echo 'hello world'")
    assert "echo 'hello world'" == task.action