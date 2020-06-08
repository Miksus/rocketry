from .csv import CsvHandler
from .adapter import TaskAdapter
from .filter import FilterAll

TASK_LOGGER = None
SCHED_LOGGER = None

def get_task_handler():
    fh = CsvHandler(
        "../log/tasks.csv",
        fields=[
            "asctime",
            "levelname",
            "task_name",
            "exc_text",
        ]
    )
    fh.addFilter(TaskFilter(include=True))
    return fh

def get_sched_handler():
    fh = CsvHandler(
        "../log/scheduler.csv",
        fields=[
            "asctime",
            "levelname",
            "task_name",
            "exc_text",
        ]
    )
    fh.addFilter(TaskFilter(include=False))
    return fh


def get_csv_handler():
    logger = logging.getLogger("asd")
    logger.addHandler(

    )
def set_csv_logger():
    global TASK_LOGGER
    logger.addHandler(
        CsvHandler(
            "proto/myfile3.csv", 
            #headers=[]
            fields=["test", "msg", "exc_info", "exc_text"], 
            kwds_csv=dict(delimiter=";")
        )
    )
    
def get_task_logger(task):
    "Get logger for task"
    return TaskAdapter(TASK_LOGGER, {"task": task, "task_name": task.name})