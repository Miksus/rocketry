from rocketry.tasks import CommandTask

def test_construct(session):
    task = CommandTask(command="echo 'hello world'", session=session)
    assert "echo 'hello world'" == task.command
