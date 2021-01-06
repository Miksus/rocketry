from .schedule import Scheduler, MultiScheduler
#from .task import FuncTask, JupyterTask, CommandTask, ScriptTask
from . import task

from . import time
#from . import event
from . import schedule
from . import conditions
#from .tools.session import session

#from .log import CsvHandler

import logging as _logging

def reset():
    "Reset logging, tasks etc. to default. Useful for testing"
    task.base.clear_tasks()
    task.base.Task.get_logger().handlers = []

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