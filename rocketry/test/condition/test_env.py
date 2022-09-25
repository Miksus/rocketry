

from rocketry.conditions import (
    IsEnv
)

def test_env(session):

    cond = IsEnv("test")
    assert not cond.observe(session=session)

    session.env = "test"
    assert cond.observe(session=session)

    session.env = "prod"
    assert not cond.observe(session=session)
