

from .core import Scheduler
from ._session import Session
from ._setup import _setup_defaults

from .config import *

from .task import FuncTask
from . import (
    conditions,
    log,
    task,
    parameters,
    time
)
_setup_defaults()

session = Session()
session.set_as_default()