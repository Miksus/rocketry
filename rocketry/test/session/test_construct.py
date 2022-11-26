
import datetime
import logging
import warnings

import pytest

from rocketry import Session
from rocketry.session import Config
from rocketry.core import Task, Scheduler, BaseCondition, BaseArgument, Parameters
from rocketry.conds import true

def assert_default(session:Session):
    for cls in (Task, Scheduler, BaseCondition, BaseArgument, Parameters):
        assert cls.session is session


def test_empty():
    session = Session(config={'execution': 'async'})
    session.set_as_default()
    assert session.parameters.to_dict() == {}
    assert session.returns.to_dict() == {}
    assert session.tasks == set()

    config = session.config

    assert isinstance(config, Config)
    assert not config.silence_task_prerun
    assert not config.silence_task_logging
    assert not config.silence_cond_check
    assert config.task_pre_exist == 'raise'
    assert config.timeout == datetime.timedelta(minutes=30)
    #assert config.task_execution == 'main'

    assert session.env is None
    assert_default(session)

def test_timeout_parse():
    session = Session(config={"timeout": 0.1, 'execution': 'async'})
    assert session.config.timeout == datetime.timedelta(seconds=0.1)

    session = Session(config={"timeout": "0.1 seconds", 'execution': 'async'})
    assert session.config.timeout == datetime.timedelta(seconds=0.1)

    session = Session(config={"timeout": datetime.timedelta(seconds=0.1), 'execution': 'async'})
    assert session.config.timeout == datetime.timedelta(seconds=0.1)

def test_create():
    with warnings.catch_warnings():
        warnings.simplefilter("error")

        s = Session(config=Config(task_priority=10, execution="async"))
        assert s.config.task_priority == 10

        s = Session(config=dict(task_priority=10, execution='async'))
        assert s.config.task_priority == 10

        Session(config={'execution': 'async'})

        s = Session(parameters={"x": 5}, config={'execution': 'async'})
        assert s.parameters == Parameters({"x": 5})
        s = Session(parameters=Parameters({"x": 5}), config={'execution': 'async'})
        assert s.parameters == Parameters({"x": 5})

    Session(config=None)

    Session()

    with pytest.raises(TypeError):
        Session(config="invalid")

def test_logging_level():
    task_logger = logging.getLogger("rocketry.task")
    task_logger.setLevel(logging.INFO)
    with warnings.catch_warnings():
        warnings.simplefilter("error")

        # Should not raise warning
        s = Session(config={'execution': 'async'})
        s.config.shut_cond = true
        s.start()

    task_logger.setLevel(logging.DEBUG)
    with warnings.catch_warnings():
        warnings.simplefilter("error")

        # Should not raise warning
        s = Session(config={'execution': 'async'})
        s.config.shut_cond = true
        s.start()

    task_logger.setLevel(logging.WARNING)
    with pytest.warns(UserWarning):
        s = Session(config={'execution': 'async'})
        s.config.shut_cond = true
        s.start()

    # Level is changed to INFO
    assert task_logger.getEffectiveLevel() == logging.INFO
