
from .utils import DictInstanceParser
from .task import parse_tasks
from redengine.core.parameters import Parameters
from redengine.core import Scheduler

parse_scheduler = DictInstanceParser(
    classes={},
    subparsers={
        "tasks": parse_tasks,
        "parameters": lambda d, **kwargs: Parameters(**d),
    },
    default=Scheduler
)