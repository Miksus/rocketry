
from .session import Session
from .core import Scheduler

from ._setup import _setup_defaults
from . import (
    conditions,
    log,
    
    arguments,
    time,
    tasks,
)
from .tasks import FuncTask
from . import views
_setup_defaults()
session = Session()
session.set_as_default()



from . import _version
__version__ = _version.get_versions()['version']
