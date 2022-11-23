from rocketry import Session
from rocketry.tasks.run_id import uuid

def test_defaults():
    s = Session(config={'execution': 'async'})
    config = s.config
    assert config.cycle_sleep == 0.1
    assert config.func_run_id is uuid
