
from atlas.core import Task

from ._strategy import CLS_STRATEGIES, CLS_STRATEGY_CONFIGS
from .condition import parse_condition
from .task import parse_task
from atlas.conditions import AlwaysFalse, DependSuccess

from .utils import ParserPicker, DictInstanceParser

from logging.config import dictConfig

def parse_tasks(conf, resources=None, **kwargs) -> list:
    if conf is None:
        return []

    if isinstance(conf, dict):
        tasks = []
        for name, task_conf in conf.items():
            task_conf["name"] = name
            tasks.append(parse_task(task_conf))
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
                tasks.append(parse_task(task_conf))
        return tasks

    else:
        raise TypeError

def _create_sequence(tasks, start_cond=None):
    session = Task.session # TODO: Get somewhere else the session
    for i, task in enumerate(tasks):
        task = session.get_task(task)
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

        parent_task = session.get_task(tasks[i-1])

        if is_not_start_cond_set:
            task.start_cond = DependSuccess(task=task, depend_task=parent_task)
        else:
            task.start_cond &= DependSuccess(task=task, depend_task=parent_task)

def parse_clear_existing(clear, **kwargs):
    if clear:
        # TODO: Get somewhere else the session
        Task.session.clear()

def parse_logging(conf, **kwargs):
    dictConfig(conf)

def parse_sequences(conf, resources):
    resources["sequences"] = {}
    for seq_name, seq_conf in conf.items():
        tasks = parse_tasks(seq_conf["tasks"])
        start_cond = seq_conf.get("start_cond", None)
        if start_cond:
            start_cond = parse_condition(start_cond)
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
        resources["strategies"][name] = parse_strategy(strat_conf)

parse_strategy = DictInstanceParser(
    classes=CLS_STRATEGIES,
    subparsers={
        "config": DictInstanceParser(classes=CLS_STRATEGY_CONFIGS),
    }
)