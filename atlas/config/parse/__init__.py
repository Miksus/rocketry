
# Parsing
from .params import parse_params
from .scheduler import parse_scheduler
from .strategy import parse_strategy
from logging.config import dictConfig as parse_logging

from atlas.core.task import clear_tasks
from atlas.core.schedule import clear_schedulers
from atlas.core.parameters import clear_parameters

# Reading config files
from pybox.io import read_yaml
from pathlib import Path

def parse_dict(conf):
    clear = conf.get("clear_existing", True)
    if clear:
        clear_tasks()
        clear_schedulers()
        clear_parameters()


    sched_conf = conf.get("scheduler", None)
    #task_conf = conf.get("tasks", None)
    #maintain_conf = conf.get("tasks", None)
    param_conf = conf.get("parameters", None)
    strategy_conf = conf.get("strategy", None)
    log_conf = conf.get("logging", None)

    # Sets up formatters, handlers and loggers
    if log_conf:
        parse_logging(log_conf)

    scheduler = parse_scheduler(sched_conf)


    parse_params(param_conf, scheduler=scheduler)
    parse_strategy(strategy_conf, scheduler=scheduler)
    
    return scheduler

def parse_yaml(path):
    conf = read_yaml(path)
    return parse_dict(conf)

def get_default(name):
    # From atlas/config/default
    root = Path(__file__).parent.parent / "defaults"
    path = root / (name + ".yaml")
    return parse_yaml(path)