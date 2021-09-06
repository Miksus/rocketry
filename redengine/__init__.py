

from .core import Scheduler
from ._session import Session
from ._setup import _setup_defaults

from .config import *

from .tasks import FuncTask
from . import (
    conditions,
    log,
    tasks,
    parameters,
    time
)
_setup_defaults()

session = Session()
session.set_as_default()
from . import _version
__version__ = _version.get_versions()['version']
