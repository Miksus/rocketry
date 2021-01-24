
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

def parse_dict_config(conf):
    clear = conf.get("clear_existing", True)
    if clear:
        clear_tasks()
        clear_schedulers()
        clear_parameters()


    sched_conf = conf["scheduler"]
    #task_conf = conf.get("tasks", None)
    #maintain_conf = conf.get("tasks", None)
    param_conf = conf.get("parameters", None)
    strategy_conf = conf.get("strategy", None)
    log_conf = conf.get("logging", None)

    # Sets up formatters, handlers and loggers
    if log_conf:
        parse_logging(log_conf)

    scheduler = parse_scheduler(sched_conf)

    if param_conf:
        parse_params(param_conf, scheduler=scheduler)
    if strategy_conf:
        parse_strategy(strategy_conf, scheduler=scheduler)
    
    return scheduler

def parse_yaml_config(conf):
    conf = read_yaml(yaml)
    return parse_dict_config(conf)

def parse_default_config(name):
    root = Path(__file__).parent / "defaults"
    path = root / (name + ".yaml")
    return parse_yaml_config(path)