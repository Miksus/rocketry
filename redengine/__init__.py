
from .session import Session
from .core import Scheduler

from ._setup import _setup_defaults
from .config import *
from . import (
    conditions,
    log,
    
    arguments,
    time,
    tasks,
)
from .tasks import FuncTask
from . import views
session = Session()
session.set_as_default()
_setup_defaults()


from . import _version
__version__ = _version.get_versions()['version']
