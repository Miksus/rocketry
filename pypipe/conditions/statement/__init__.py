
from .base import Statement
from .builtin import (
    TaskStarted,
    TaskFinished,
    TaskFailed,
    TaskSucceeded,
    TaskRunning,

    DependFinish,
    DependFailure,
    DependSuccess,

    RamFree,
    RamUsed,
    SchedulerCycles,
    SchedulerStarted,
)

from .utils import set_statement_defaults