from .schedule import Scheduler, MultiScheduler, Task

from .conditions import (
    HasOccurred, HasNotOccurred, Occurring,
    IsTimeOfDay, IsDaysOfWeek
)

from . import time
#from . import event
from . import schedule
from .schedule import Task

from .log import CsvHandler

import logging as _logging

def setup_logging():
    from pathlib import Path
    Path("log").mkdir(parents=True, exist_ok=True)
    handler = CsvHandler(
        "log/tasks.csv",
        fields=[
            "asctime",
            "levelname",
            "action",
            "task_name",
            "exc_text",
        ]
    )
    Task.logger.addHandler(handler)
    Task.logger.setLevel(_logging.INFO)
    print("Created log file")

#setup_logging()