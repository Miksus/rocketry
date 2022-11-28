from functools import partial

from rocketry.core.condition import (All, AlwaysFalse, AlwaysTrue, Any,
                                     BaseCondition, Not)
from rocketry.time.interval import TimeOfHour, TimeOfMinute, TimeOfMonth

from .func import FuncCond
from .meta import TaskCond
from .parameter import IsEnv, ParamExists
from .scheduler import *
from .task import *
from .time import *
