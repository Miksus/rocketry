from atlas.parse import parse_session
from pathlib import Path
from pybox.io import read_yaml

def parse_yaml(path):
    conf = read_yaml(path)
    return parse_dict(conf)

def get_default(name, scheduler_basename=None, task_basename=None):
    # From atlas/config/default
    root = Path(__file__).parent / "defaults"
    path = root / (name + ".yaml")

    conf = read_yaml(path)

    # Renaming atlas.task to task_basename
    if "logging" in conf and "loggers" in conf["logging"]:
        _rename_basenames(
            conf["logging"]["loggers"], 
            task_basename=task_basename, 
            scheduler_basename=scheduler_basename,
        )

    return parse_dict(conf)

def _rename_basenames(loggers:dict, task_basename, scheduler_basename):
    if task_basename is None and scheduler_basename is None:
        return
    for key in loggers:
        if key.startswith("atlas.task"):
            new_key = key.replace("atlas.task", task_basename)
        elif key.startswith("atlas.scheduler"):
            new_key = key.replace("atlas.scheduler", scheduler_basename)
        else:
            continue
        loggers[new_key] = loggers.pop(key)

def parse_dict(conf:dict):
    return parse_session(conf)