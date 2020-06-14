from .base import Statement

import psutil
import os
import numpy as np

@Statement(historical=True)
def task_ran(task, start=None, end=None):
    records = task.logger.get_records(start=start, end=end, action="run")
    run_times = records["asctime"].tolist()
    return run_times

@Statement(historical=True)
def task_failed(task, start, end):
    records = task.logger.get_records(start=start, end=end, action="fail")
    return not records.empty

@Statement(historical=True)
def task_succeeded(task, start, end):
    records = task.logger.get_records(start=start, end=end, action="success")
    return not records.empty

@Statement(historical=True)
def task_finished(task, start, end):
    records = task.logger.get_records(start=start, end=end, action=["success", "fail"])
    return not records.empty

@Statement()
def task_running(task):
    "Check whether "
    record = task.logger.get_latest()
    return record["action"] == "run"

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

