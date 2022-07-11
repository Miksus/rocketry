from functools import partial

from rocketry.time.interval import TimeOfHour, TimeOfMinute, TimeOfMonth

from .func import FuncCond
from .task import *
from .scheduler import *
from .time import *
from .parameter import ParamExists, IsEnv
from .meta import TaskCond

from rocketry.core.condition import AlwaysFalse, AlwaysTrue, All, Any, Not, BaseCondition
