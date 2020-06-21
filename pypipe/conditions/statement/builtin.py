from .base import Statement

import psutil
import os
import numpy as np

import logging
logger = logging.getLogger(__name__)

# Task related
@Statement(historical=True, quantitative=True)
def task_ran(task, start=None, end=None):
    records = task.logger.get_records(start=start, end=end, action="run")
    run_times = records["asctime"].tolist()
    return run_times

@Statement(historical=True, quantitative=True)
def task_failed(task, start, end):
    records = task.logger.get_records(start=start, end=end, action="fail")
    return not records.empty

@Statement(historical=True, quantitative=True)
def task_succeeded(task, start, end):
    records = task.logger.get_records(start=start, end=end, action="success")
    return not records.empty

@Statement(historical=True, quantitative=True)
def task_finished(task, start, end):
    records = task.logger.get_records(start=start, end=end, action=["success", "fail"])
    return not records.empty

@Statement()
def task_running(task):
    "Check whether "
    record = task.logger.get_latest()
    return record["action"] == "run"


# Scheduler related (useful only for maintaining or shutdown)
@Statement(quantitative=True)
def scheduler_cycles(scheduler):
    "Check whether "
    logger.debug(f"Inspecting {scheduler} (type: {type(scheduler)} cycles...")
    return scheduler.n_cycles

@Statement(historical=True)
def scheduler_started(scheduler, start, end):
    "Check whether "
    dt = scheduler.startup_time
    return start <= dt <= end


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

