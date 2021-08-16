from powerbase.parse import parse_session
from pathlib import Path
from pybox.io import read_yaml

DEFAULT_BASENAME_TASKS = "powerbase.task"
DEFAULT_BASENAME_SCHEDULER = "powerbase.scheduler"

def parse_yaml(path):
    conf = read_yaml(path)
    return parse_dict(conf)

def get_default(name:str, scheduler_basename:str=None, task_basename:str=None):
    """Get premade configuration. 

    Parameters
    ----------
    name : str
        Scheme name. See lib/powerbase/config/defaults.
    scheduler_basename : str, optional
        Name of the logger that should be used to log
        scheduler's activity. The 'powerbase.scheduler'
        from the config scheme is renamed as so, by default 
        None
    task_basename : str, optional
        Name of the logger that should be used to log
        tasks' activity. The 'powerbase.tasks'
        from the config scheme is renamed as so, by default 
        None
    """    
    # From powerbase/config/default
    root = Path(__file__).parent / "defaults"
    path = root / (name + ".yaml")

    conf = read_yaml(path)

    # Renaming powerbase.task to task_basename
    is_loggers_specified = "loggers" in conf.get("logging", {})
    if is_loggers_specified:
        _rename_basenames(
            conf["logging"]["loggers"], 
            task_basename=task_basename, 
            scheduler_basename=scheduler_basename,
        )

    return parse_dict(conf)

def _rename_basenames(loggers:dict, task_basename, scheduler_basename):
    """Rename all loggers that start with 'powerbase.task' and powerbase.scheduler
    in the default configuration.
    """
    no_change_in_basenames = (
        task_basename in (DEFAULT_BASENAME_TASKS, None) 
        and scheduler_basename in (DEFAULT_BASENAME_SCHEDULER, None)
    )
    if no_change_in_basenames:
        # Do nothing, the config's loggers need not to be renamed.
        return
    
    # NOTE: We are modifying the loggers dictionary thus we need to make 
    # a copy of the keys.
    for key in list(loggers):
        if key.startswith(DEFAULT_BASENAME_TASKS):
            new_key = key.replace(DEFAULT_BASENAME_TASKS, task_basename)
        elif key.startswith(DEFAULT_BASENAME_SCHEDULER):
            new_key = key.replace(DEFAULT_BASENAME_SCHEDULER, scheduler_basename)
        else:
            continue
        loggers[new_key] = loggers.pop(key)

def parse_dict(conf:dict):
    return parse_session(conf)