
from atlas.core.task import get_task
from atlas.conditions import DependSuccess
from atlas.parse import parse_condition_clause
from atlas.conditions import AlwaysFalse

def _create_sequence(*tasks, start_cond=None):
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

def parse_sequence_from_dict(conf:dict):
    "Parse one sequence"
    start_cond = seq_conf.get("start_cond", None)

def parse_sequence(conf:dict):
    "Parse one sequence"
    tasks = conf["tasks"]
    
    start_cond = conf.get("start_cond", None)
    if start_cond:
        start_cond = parse_condition_clause(start_cond)

    # Sets start conditions and other parameters
    # does not create new tasks
    _create_sequence(*tasks, start_cond=start_cond)
    return tasks


def parse_sequences(conf:dict, resources:dict):
    """[summary]
    Example:
    --------
        end-of-day:
            start_cond: 'daily between 22:00 and 08:00'
            tasks:
            - reinstall_atlas
            - reinstall_pybox
            - clear_logging
            - restart
    """
    resources["sequences"] = {}
    for seq_name, seq_conf in conf.items():
        resources["sequences"][seq_name] = parse_sequence(seq_conf)
        continue
