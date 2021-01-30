# Parsing
#from .params import parse_session_params
#from .scheduler import parse_scheduler
#from .sequences import parse_sequences, _create_sequence
#from .strategies import parse_strategies
#from .tasks import parse_tasks
from atlas.parse import parse_condition_clause

from .parser import StaticParser, Field, DictInstanceParser, ParserPicker
from atlas.parse import parse_condition_clause
from logging.config import dictConfig

from atlas.core.task import clear_tasks, get_task
from atlas.core.schedule import clear_schedulers
from atlas.core.parameters import clear_parameters, Parameters

from atlas.core import MultiScheduler, Scheduler
from atlas.core.parameters import GLOBAL_PARAMETERS
from atlas.core.parameters import Parameters

from atlas.core.task import CLS_TASKS, Task
from atlas.core.conditions.base import CLS_CONDITIONS
from .strategy import CLS_STRATEGIES, CLS_STRATEGY_CONFIGS

from atlas.task import FuncTask
from atlas.conditions import AlwaysFalse, DependSuccess

import importlib

"""syntax
clear_existing: True|False

parameters:
    mode: test

tasks:
    my-task-1:
        class: FuncTask
        func: maintainers.print_run_log
        ...
    my-task-2
        class: ScriptTask
        path: path/to/script.py
        ...
    my-task-3
        class: PipInstall
        ....

sequences:
    run-seq-1:
        start_cond: daily
        tasks:
            - my-task-1
            - my-task-2



scheduler:
    type: 'multi'|'single'

    tasks:
    - run-seq-1
    - my-task-3
    strategies:
    - personal

"""

def _create_sequence(tasks, start_cond=None):
    for i, task in enumerate(tasks):
        task = get_task(task)
        is_not_start_cond_set = task.start_cond == AlwaysFalse()
        if i == 0:
            # Father (Mother) of the sequence
            # TODO: Overriding default start condition
            # should be able to do more clearly
            if start_cond is not None:
                if is_not_start_cond_set:
                    task.start_cond = start_cond
                else:
                    task.start_cond &= start_cond
            continue

        parent_task = get_task(tasks[i-1])

        if is_not_start_cond_set:
            task.start_cond = DependSuccess(task=task, depend_task=parent_task)
        else:
            task.start_cond &= DependSuccess(task=task, depend_task=parent_task)


def parse_session_params(conf:dict, **kwargs) -> None:
    """Parse the parameters section of a config
    """
    if not conf:
        return
    params = Parameters(**conf)
    GLOBAL_PARAMETERS.update(params)


def parse_clear_existing(clear, **kwargs):
    if clear:
        clear_tasks()
        clear_schedulers()
        clear_parameters()

def parse_logging(conf, **kwargs):
    dictConfig(conf)


COND_PARSER = ParserPicker(
    {
        str: parse_condition_clause,
        dict: DictInstanceParser(classes=CLS_CONDITIONS),
    }
) 

def parse_tasks(conf, resources=None, **kwargs) -> list:
    if conf is None:
        return []

    if isinstance(conf, dict):
        tasks = []
        for name, task_conf in conf.items():
            task_conf["name"] = name
            tasks.append(TASK_PARSER(task_conf))
        return tasks

    elif isinstance(conf, list):
        tasks = []
        strategies = resources.get("strategies", []) if resources is not None else []
        sequences = resources.get("sequences", []) if resources is not None else []
        for task_conf in conf:
            if task_conf in strategies:
                tasks += parse_tasks(strategies[task_conf]())
            elif task_conf in sequences:
                tasks += parse_tasks(sequences[task_conf])
            elif isinstance(task_conf, Task):
                tasks.append(task_conf)
            else:
                tasks.append(TASK_PARSER(task_conf))
        return tasks

    else:
        raise TypeError

def _parse_func_task(**kwargs):

    module, func = kwargs.pop("func").rsplit('.', 1)
    mdl = importlib.import_module(module)
    func = getattr(mdl, func)
    return FuncTask(**kwargs, func=func)

def parse_sequences(conf, resources):
    resources["sequences"] = {}
    for seq_name, seq_conf in conf.items():
        tasks = parse_tasks(seq_conf["tasks"])
        start_cond = seq_conf.get("start_cond", None)
        if start_cond:
            start_cond = COND_PARSER(start_cond)
            if isinstance(tasks[0].start_cond, AlwaysFalse):
                tasks[0].start_cond = start_cond
            else:
                tasks[0].start_cond &= start_cond

        _create_sequence(tasks)
        resources["sequences"][seq_name] = tasks
        continue

def parse_strategies(conf, resources):
    resources["strategies"] = {}
    for name, strat_conf in conf.items():
        resources["strategies"][name] = STRATEGY_PARSER(strat_conf)

# Parse one task
TASK_PARSER = ParserPicker(
    {
        dict:DictInstanceParser(
            classes={**CLS_TASKS, **{"FuncTask": _parse_func_task}}, 
            subparsers={
                "start_cond": COND_PARSER,
                "end_cond": COND_PARSER,
            },
        ),
        str: get_task
    }
)

SCHED_PARSER = DictInstanceParser(
    classes={"multi": MultiScheduler, "single": Scheduler},
    subparsers={
        "tasks": parse_tasks,
        "maintainer_tasks": parse_tasks,
        "shutdown_tasks": parse_tasks,
        "startup_tasks": parse_tasks,
        "parameters": lambda d, resources: Parameters(**d),
    },
    default=MultiScheduler
)

STRATEGY_PARSER = DictInstanceParser(
    classes=CLS_STRATEGIES,
    subparsers={
        "config": DictInstanceParser(classes=CLS_STRATEGY_CONFIGS),
    }
)


PARSER = StaticParser(
    Field("clear_existing", parse_clear_existing, if_missing="ignore", types=(bool,)),
    Field("logging",        parse_logging,        if_missing="ignore"),
    Field("parameters",     parse_session_params, if_missing="ignore", types=(dict,)),
    Field("tasks",          parse_tasks,          if_missing="ignore", types=(dict,)),
    Field("sequences",      parse_sequences,      if_missing="ignore"),
    Field("strategies",     parse_strategies,     if_missing="ignore"),
    Field("scheduler",      SCHED_PARSER,         if_missing="ignore"),
    on_extra="ignore", 
    #resources={"strategies": []}
    # Ps: I know this spacing is against PEP8, but do I care? No.
)


def parse_dict(conf):
    return PARSER(conf)