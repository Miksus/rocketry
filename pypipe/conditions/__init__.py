from .time import (
    IsTimeOfDay, 
    IsDaysOfWeek,
    is_weekend,
)

from .statement import *
#(
#    Statement,
#    task_ran,
#    TaskFailed,
#    TaskSucceeded,
#    ram_free,
#    ram_used,
#    task_running
#)


from .utils import set_defaults
from .base import AlwaysTrue, AlwaysFalse, All, Any, Not