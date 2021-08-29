
from .utils import ParserPicker, DictInstanceParser
from .misc import parse_tasks

from powerbase.core.parameters import Parameters
from powerbase.core import Scheduler

parse_scheduler = DictInstanceParser(
    classes={},
    subparsers={
        "tasks": parse_tasks,
        "parameters": lambda d, **kwargs: Parameters(**d),
    },
    default=Scheduler
)