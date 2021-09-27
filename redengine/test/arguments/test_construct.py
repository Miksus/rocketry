
from redengine.arguments import FuncArg, Arg
from redengine import Session

import pytest

def test_arg(session):
    Arg.put_session(my_param_1=1, my_param_2=2)
    assert {"my_param_1": 1, "my_param_2": 2} == dict(session.parameters)

def test_funcarg_from_decor(session):

    @FuncArg.put_session("my_param_1")
    def myfunc1(session):
        assert isinstance(session, Session)
        return 1

    @FuncArg.put_session("my_param_2")
    def myfunc2():
        return 2

    @FuncArg.put_session()
    def my_param_3():
        return 3

    assert {"my_param_1": 1, "my_param_2": 2, "my_param_3": 3} == dict(session.parameters)

    # This should lead to error though:
    with pytest.raises(TypeError):
        @FuncArg.put_session
        def my_param_4():
            return 3