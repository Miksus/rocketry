import warnings

import pytest
from rocketry import Session

def test_shutdown(session):
    assert not session.scheduler._flag_shutdown.is_set()
    with pytest.warns(DeprecationWarning):
        session.shutdown()
    assert session.scheduler._flag_shutdown.is_set()

def test_no_execution_method():

    with pytest.warns(FutureWarning):
        Session()

    with warnings.catch_warnings():
        warnings.simplefilter("error")

        # Test the following won't warn
        Session(config=dict(task_execution="process"))
        Session(config=dict(task_execution="thread"))
        Session(config=dict(task_execution="main"))
        Session(config=dict(task_execution="async"))
