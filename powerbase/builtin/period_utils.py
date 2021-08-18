from powerbase.parse import add_condition_parser

from powerbase.conditions import (
    TaskFinished, 
    TaskFailed, 
    TaskSucceeded, 
    TaskRunning,
    TaskStarted,

    TaskExecutable,

    DependSuccess,
    DependFinish,
    DependFailure,

    AlwaysTrue,
    AlwaysFalse,

    IsPeriod,
    IsEnv,
)

from powerbase.core.conditions.base import BaseCondition
from powerbase.time import (
    TimeOfWeek,
    TimeOfDay,
    TimeOfHour,
    TimeOfMinute,
    TimeDelta,
)

TIME_CLASSES = {
    "daily": TimeOfDay,
    "weekly": TimeOfWeek,
    "hourly": TimeOfHour,
    "minutely": TimeOfMinute,

    "day": TimeOfDay,
    "week": TimeOfWeek,
    "hour": TimeOfHour,
    "minute": TimeOfMinute,
}

# Utility funcs
def get_between(type_, start, end):
    type_ = type_.lower()
    cls = TIME_CLASSES[type_]
    return cls(start, end)

def get_after(type_, start):
    type_ = type_.lower()
    cls = TIME_CLASSES[type_]
    return cls(start, None)

def get_before(type_, end):
    type_ = type_.lower()
    cls = TIME_CLASSES[type_]
    return cls(None, end)

def get_full_cycle(type_, start=None):
    type_ = type_.lower()
    cls = TIME_CLASSES[type_]
    return cls(start, start)
