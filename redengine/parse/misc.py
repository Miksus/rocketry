
from logging.config import dictConfig

from redengine.core import Task

from .condition import parse_condition
from redengine.conditions import AlwaysFalse, DependSuccess


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
