
from pypipe.core.task import base
from pypipe.core.conditions import Statement

import psutil
import os
import datetime
import numpy as np

# Scheduler related (useful only for maintaining or shutdown)
@Statement.from_func(historical=False, quantitative=True)
def SchedulerCycles(scheduler, **kwargs):
    "Check whether "
    logger.debug(f"Inspecting {scheduler} (type: {type(scheduler)} cycles...")
    return scheduler.n_cycles

@Statement.from_func(historical=True, quantitative=False)
def SchedulerStarted(scheduler, _start_, _end_):
    "Check whether "
    dt = scheduler.startup_time
    return _start_ <= dt <= _end_

