from .session import Session
from .application import Rocketry, Grouper
from .core import Scheduler

try:
    from ._version import *
except ImportError:
    # Package was not built the standard way
    __version__ = version = '0.0.0.UNKNOWN'
    __version_tuple__ = version_tuple = (0, 0, 0, 'UNKNOWN', '')

from ._setup import _setup_defaults
from . import (
    conditions,
    log,

    args,
    time,
    tasks,
)
from .tasks import FuncTask
_setup_defaults()
session = Session(config={"execution": "process"})
session.set_as_default()
