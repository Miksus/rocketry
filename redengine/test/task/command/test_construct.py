
from redengine.tasks import CommandTask

def test_construct():
    task = CommandTask("echo 'hello world'")
    assert "echo 'hello world'" == task.action