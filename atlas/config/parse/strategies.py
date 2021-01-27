

from ..strategy import TASK_STRATEGIES, TASK_CONFIG_STRATEGIES, PARAM_STRATEGIES

def parse_strategy_config(conf:dict):
    if not conf:
        return {}
    if "class" in conf:
        # Use ConfigFinder
        type_ = conf.pop("class")
        cls = TASK_CONFIG_STRATEGIES[type_]
        return cls(**conf)
    else:
        return StaticConfig(conf)

def parse_strategy(conf:dict):
    """Parse a task strategy

    A strategy is a configurable callable that 
    produces a list of tasks or parameters. For
    task strategies, it should have an argument 
    in init for config which defines how the 
    tasks are configured.

    Example:
    --------
        {
            "class": "ProjectFinder",
            "path": "path/to/project",
            # Optional
            "config": {
                "class": "FileConfig",
                "filename": "config.yaml",
            }
        }
    """
    cls_name = conf.pop("class")
    task_config = conf.pop("config", None)
    task_config = parse_strategy_config(task_config)

    # cls is a TaskFinder and config
    cls = TASK_STRATEGIES[cls_name]
    return cls(**conf, config=task_config)

def parse_strategies(conf, resources):
    """Parse strategy part of the config

    Example:
    --------
        {
            "strategy.find-tasks": {"class": "ProjectFinder", ...}
        }
    """
    resources["strategies"] = {}
    for name, strat_conf in conf.items():
        resources["strategies"][name] = parse_strategy(strat_conf)