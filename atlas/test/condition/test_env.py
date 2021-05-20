

from atlas.conditions import (
    IsEnv
)
from atlas import session
from atlas.core.conditions import Statement, Comparable, Historical

import pytest


def test_env():
    
    cond = IsEnv("test")
    assert not bool(cond)

    session.env = "test"
    assert bool(cond)

    session.env = "prod"
    assert not bool(cond)
