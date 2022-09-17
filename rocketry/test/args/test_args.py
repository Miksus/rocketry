import os, sys
import pytest
from rocketry.args import Private, SimpleArg, FuncArg, Arg, EnvArg, CliArg
from rocketry.tasks import FuncTask

def test_simple():
    arg = SimpleArg("a value")
    assert arg.get_value() == "a value"

def test_func():
    def get_value():
        return 'a value'

    arg = FuncArg(get_value)
    assert arg.get_value() == "a value"

def test_arg(session):
    
    session.parameters['myarg'] = 'a value'
    arg = Arg('myarg')
    assert arg.get_value(session=session) == "a value"

    assert Arg('missing', default="a value").get_value(session=session) == "a value"
    with pytest.raises(KeyError):
        arg = Arg('missing')
        arg.get_value(session=session)

def test_env_arg():
    os.environ['ROCKETRY_TEST_VARIABLE'] = "a value"
    arg = EnvArg('ROCKETRY_TEST_VARIABLE')
    assert arg.get_value() == "a value"

    arg = EnvArg('ROCKETRY_NOT_SET', default="a value 2")
    assert arg.get_value() == "a value 2"

    with pytest.raises(KeyError):
        arg = EnvArg('ROCKETRY_NOT_SET')
        arg.get_value()

def test_cli_arg():
    assert CliArg.cli_args == sys.argv
    orig_arg = CliArg.cli_args
    try:
        CliArg.cli_args = ['python', 'myfile.py', '--myparam', 'a value']

        arg = CliArg('--myparam')
        assert arg.get_value() == "a value"
        assert CliArg('--invalid', default="a value").get_value() == "a value"
        with pytest.raises(KeyError):
            CliArg('--invalid').get_value()
    finally:
        CliArg.cli_args = orig_arg

def test_private():
    task = FuncTask(lambda x: x)

    value = Private("my secret")
    assert value.get_value() == "*****"
    assert value.get_value(task=task) == "my secret"
    assert str(value) == "*****"
    assert repr(value) == "Private(*****)"

@pytest.mark.parametrize("obj", [Arg('x'), SimpleArg('value'), Private('value'), FuncArg(lambda: None)])
def test_kwargs(obj, session):
    session.parameters['x'] = None
    obj.get_value(dont_use="something", session=session)