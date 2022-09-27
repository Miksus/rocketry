import pytest
from rocketry.args import SimpleArg, Arg, EnvArg, CliArg

def test_equal():
    assert SimpleArg("A") != SimpleArg("B")
    assert SimpleArg("A") != SimpleArg("B")
    assert SimpleArg("A") == SimpleArg("A")

def test_pipeline(session):
    session.parameters['found'] = "a value"
    session.parameters['not_reached'] = "a value 2"

    comb_arg = CliArg("--this-is-missing") >> EnvArg('ROCKETRY_MISSING') >> Arg('missing') >> Arg('found') >> Arg('not_reached')
    assert comb_arg.get_value(session=session) == "a value"

    comb_arg = CliArg("--this-is-missing", default="a value 2") >> EnvArg('ROCKETRY_MISSING') >> Arg('missing') >> Arg('found') >> Arg('not_reached')
    assert comb_arg.get_value(session=session) == "a value 2"

    with pytest.raises(KeyError):
        (CliArg("--this-is-missing") >> EnvArg('ROCKETRY_MISSING')).get_value(session=session)
    with pytest.raises(TypeError):
        CliArg("--this-is-missing", default="a value 2") >> 4
