from .session import Session
from .application import Rocketry, Grouper
from . import _version
from .core import Scheduler

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


__version__ = _version.get_versions()['version']
