from .base import Observation

import psutil
import os
import numpy as np

@Observation(historical=True)
def task_ran(task, start, end):
    records = task.logger.get_records(start=start, end=end, action="run")
    return not records.empty

@Observation(historical=True)
def task_failed(task, start, end):
    records = task.logger.get_records(start=start, end=end, action="fail")
    return not records.empty

@Observation(historical=True)
def task_succeeded(task, start, end):
    records = task.logger.get_records(start=start, end=end, action="success")
    return not records.empty

@Observation(historical=True)
def task_finished(task, start, end):
    records = task.logger.get_records(start=start, end=end, action=["success", "fail"])
    return not records.empty

@Observation()
def task_running(task):
    "Check whether "
    record = task.logger.get_latest()
    return record["action"] == "run"

@Observation(quantitative=True)
def ram_free(absolute=False):
    "Check whether "
    memory = psutil.virtual_memory()
    if not absolute:
        return 1 - memory.percent / 100
    else:
        return memory.available

@Observation(quantitative=True)
def ram_used(absolute=False):
    "Check whether "
    memory = psutil.virtual_memory()
    if not absolute:
        return memory.percent / 100
    else:
        return memory.used

@Observation()
def file_exists(filename):
    return os.path.exists(filename)

