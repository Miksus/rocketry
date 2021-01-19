
from atlas.conditions import (
    TaskFinished, 
    TaskFailed, 
    TaskSucceeded, 
    TaskRunning,

    TaskExecutable,

    DependSuccess,
    DependFinish,
    DependFailure,

    AlwaysTrue,
    AlwaysFalse,

    IsPeriod,
)

from atlas.core.conditions.base import BaseCondition
from atlas.time import (
    TimeOfDay,
    DaysOfWeek,
    TimeOfHour,

    TimeDelta,
)

import re

def get_between(type_, start, end):
    type_ = type_.lower()
    cls = {
        "daily": TimeOfDay,
        "weekly": DaysOfWeek,
        "hourly": TimeOfHour,

        "day": TimeOfDay,
        "week": DaysOfWeek,
        "hour": TimeOfHour,
    }[type_]
    return cls(start, end)

def get_after(type_, start):
    type_ = type_.lower()
    cls = {
        "daily": TimeOfDay,
        "weekly": DaysOfWeek,
        "hourly": TimeOfHour,

        "day": TimeOfDay,
        "week": DaysOfWeek,
        "hour": TimeOfHour,
    }[type_]
    return cls(start, None)

def get_before(type_, end):
    type_ = type_.lower()
    cls = {
        "daily": TimeOfDay,
        "weekly": DaysOfWeek,
        "hourly": TimeOfHour,

        "day": TimeOfDay,
        "week": DaysOfWeek,
        "hour": TimeOfHour,
    }[type_]
    return cls(None, end)

def get_full_cycle(type_, starting=None):
    type_ = type_.lower()
    cls = {
        "daily": TimeOfDay,
        "weekly": DaysOfWeek,
        "hourly": TimeOfHour,
    
        "day": TimeOfDay,
        "week": DaysOfWeek,
        "hour": TimeOfHour,
    }[type_]
    return cls(starting, starting)

# TODO: How to distinquise between the actual task and dependency? Modify the set_default_task

EXPRESSIONS = [
    # Another task ran as
    # TODO: These are always true after one run
    (r"after '(?P<depend_task>.+)' succeeded",        DependSuccess),
    (r"after '(?P<depend_task>.+)' finished",  DependFinish),
    (r"after '(?P<depend_task>.+)' failed",    DependFailure),
    (r"after '(?P<depend_task>.+)'",      DependSuccess),
    
    (r"while '(?P<task>.+)' is running",   TaskRunning), 
    # (r"after started '(?P<task>.+)'",   TaskStarted), # TODO

    # Run the task itself during specified 
    # (the task itself has not previously run during given period)
    (
        # TODO
        r"(run )?(?P<type_>monthly|weekly|daily|hourly|minutely) starting (?P<start>.+)", 
        lambda type_, start: TaskExecutable(period=get_full_cycle(type_, starting=start))
    ),
    (
        r"(run )?(?P<type_>monthly|weekly|daily|hourly|minutely) between (?P<start>.+) and (?P<end>.+)", 
        lambda type_, start, end: TaskExecutable(period=get_between(type_, start, end))
    ),
    (
        r"(run )?(?P<type_>monthly|weekly|daily|hourly|minutely) after (?P<start>.+)", 
        lambda type_, start: TaskExecutable(period=get_after(type_, start))
    ),
    (
        r"(run )?(?P<type_>monthly|weekly|daily|hourly|minutely) before (?P<end>.+)",
        lambda type_, end: TaskExecutable(period=get_before(type_, end))
    ),
    (
        r"(run )?(?P<type_>monthly|weekly|daily|hourly|minutely)", 
        lambda type_: TaskExecutable(period=get_full_cycle(type_))
    ),
    (
        r"(run )?every (?P<value>.+)",
        lambda value: TaskExecutable(period=TimeDelta(value))
    ),

    # Time is as specified (TODO)
    (
        r"time of (?P<type_>month|week|day|hour|minute) between (?P<start>.+) and (?P<end>.+)",
        lambda type_, start, end: IsPeriod(period=get_between(type_ + "ly", start, end))
    ),
    (
        r"time of (?P<type_>month|week|day|hour|minute) after (?P<start>.+)",
        lambda type_, start: IsPeriod(period=get_after(type_ + "ly", start))
    ),
    (
        r"time of (?P<type_>month|week|day|hour|minute) before (?P<end>.+)", 
        lambda type_, end: IsPeriod(period=get_before(type_, end))
    ),

    # Failure/Success
    #(
    #    # TODO
    #    r"try (?P<value>[0-9]+) times", 
    #    lambda value: TaskFailedConsecutively() <= value
    #),

    # Parameters
    #(
    #    # TODO
    #    r"(global )?parameter '(?P<param>.+)' set as '(?P<value>.+)'", 
    #    lambda param, value: HasGlobalParameter(param) == value
    #),

    (r"always true", lambda:AlwaysTrue()),
    (r"always false", lambda:AlwaysFalse()),
]

def parse_statement(s:str) -> BaseCondition:
    "Parse single statement"
    expressions = EXPRESSIONS
    for expr, func in expressions:
        res = re.search(expr, s, flags=re.IGNORECASE)
        if res:
            # Found the right regex expression
            output =  func(**res.groupdict())
            break
    else:
        raise ValueError(f"Unknown conversion for: {s}")
    return output
