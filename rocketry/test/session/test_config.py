from rocketry import Session

def test_defaults():
    s = Session(config={'task_execution': 'async'})
    config = s.config
    assert config.cycle_sleep == 0.1