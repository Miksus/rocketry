
from pypipe.core.task import base
from pypipe.core.conditions import Statement

import psutil
import os
import datetime
import numpy as np

# Scheduler related (useful only for maintaining or shutdown)
@Statement.from_func(historical=False, quantitative=True)
def SchedulerCycles(_scheduler_, **kwargs):
    "Check whether "
    return _scheduler_.n_cycles

@Statement.from_func(historical=True, quantitative=False)
def SchedulerStarted(_scheduler_, _start_, _end_, **kwargs):
    "Check whether "
    dt = _scheduler_.startup_time
    return _start_ <= dt <= _end_

@Statement.from_func(historical=False, quantitative=True)
def TasksAlive(_scheduler_, **kwargs):
    "Check whether "
    alive_tasks = [_scheduler_.is_alive(task) for task in _scheduler_.tasks]
    return alive_tasks
