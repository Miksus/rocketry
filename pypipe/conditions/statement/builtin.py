
from pypipe.task import base
from .base import Statement

import psutil
import os
import numpy as np

import logging
logger = logging.getLogger(__name__)

# Task related
@Statement(historical=True, quantitative=True)
def task_ran(task, _start_=None, _end_=None):
    records = base.get_task(task).logger.get_records(start=_start_, end=_end_, action="run")
    run_times = records["asctime"].tolist()
    return run_times

@Statement(historical=True, quantitative=True)
def task_failed(task, _start_, _end_):
    records = base.get_task(task).logger.get_records(start=_start_, end=_end_, action="fail")
    return records

@Statement(historical=True, quantitative=True)
def task_succeeded(task, _start_, _end_):
    records = base.get_task(task).logger.get_records(start=_start_, end=_end_, action="success")
    return records

@Statement(historical=True, quantitative=True)
def task_finished(task, _start_, _end_):
    records = base.get_task(task).logger.get_records(start=_start_, end=_end_, action=["success", "fail"])
    return records

@Statement()
def task_running(task):
    "Check whether "
    record = get_task(task).logger.get_latest()
    return record["action"] == "run"


# Scheduler related (useful only for maintaining or shutdown)
@Statement(quantitative=True)
def scheduler_cycles(scheduler):
    "Check whether "
    logger.debug(f"Inspecting {scheduler} (type: {type(scheduler)} cycles...")
    return scheduler.n_cycles

@Statement(historical=True)
def scheduler_started(scheduler, _start_, _end_):
    "Check whether "
    dt = scheduler.startup_time
    return _start_ <= dt <= _end_


# OS related
@Statement(quantitative=True)
def ram_free(absolute=False):
    "Check whether "
    memory = psutil.virtual_memory()
    if not absolute:
        return 1 - memory.percent / 100
    else:
        return memory.available

@Statement(quantitative=True)
def ram_used(absolute=False):
    "Check whether "
    memory = psutil.virtual_memory()
    if not absolute:
        return memory.percent / 100
    else:
        return memory.used

@Statement()
def file_exists(filename):
    return os.path.exists(filename)

# GIT
@Statement(historical=True)
def last_commited(_start_, _end_, repo=None):
    repo = Repo(repo)
    last_commit = next(iter(repo.iter_commits()))
    dt = pd.Timestamp(last_commit.committed_date, unit="s")
    return _start_ <= dt <= _end_