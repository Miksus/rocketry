from rocketry.args import Private, SimpleArg
from rocketry.tasks import FuncTask

def test_private():
    task = FuncTask(lambda x: x)

    value = Private("my secret")
    assert value.get_value() == "*****"
    assert value.get_value(task=task) == "my secret"
    assert str(value) == "*****"
    assert repr(value) == "Private(*****)"

def test_simple():
    task = FuncTask(lambda x: x)

    value = SimpleArg("my secret")
    assert value.get_value() == "my secret"
    assert value.get_value(task=task) == "my secret"
