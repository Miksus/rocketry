

from powerbase.conditions import (
    IsEnv
)
from powerbase.core.conditions import Statement, Comparable, Historical

import pytest


def test_env(session):
    
    cond = IsEnv("test")
    assert not bool(cond)

    session.env = "test"
    assert bool(cond)

    session.env = "prod"
    assert not bool(cond)
