from rocketry.args import Private, SimpleArg
from rocketry.tasks import FuncTask

def test_equal():
    assert SimpleArg("A") != SimpleArg("B")
    assert not (SimpleArg("A") == SimpleArg("B"))
    assert SimpleArg("A") == SimpleArg("A")