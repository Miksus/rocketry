
from .utils import ParserPicker, DictInstanceParser
from .misc import parse_tasks

from atlas.core.parameters import Parameters
from atlas.core import Scheduler

parse_scheduler = DictInstanceParser(
    classes={},
    subparsers={
        "tasks": parse_tasks,
        "parameters": lambda d, resources: Parameters(**d),
    },
    default=Scheduler
)