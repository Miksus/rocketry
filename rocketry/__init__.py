from .application import Grouper, Rocketry
from .core import Scheduler
from .session import Session

try:
    from ._version import *
except ImportError:
    # Package was not built the standard way
    __version__ = version = '0.0.0.UNKNOWN'
    __version_tuple__ = version_tuple = (0, 0, 0, 'UNKNOWN', '')

from . import args, conditions, log, tasks, time
from ._setup import _setup_defaults
from .tasks import FuncTask

_setup_defaults()
session = Session(config={"execution": "process"})
session.set_as_default()
