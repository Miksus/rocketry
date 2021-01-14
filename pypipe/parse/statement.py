
from pypipe.conditions import (
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

from pypipe.core.conditions.base import BaseCondition
from pypipe.time import (
    TimeOfDay,
    DaysOfWeek,
    TimeOfHour,
)

import re

def get_between(type_, start, end):
    type_ = type_.lower()
    cls = {
        "daily": TimeOfDay,
        "weekly": DaysOfWeek,
        "hourly": TimeOfHour,
    }[type_]
    return cls(start, end)

def get_after(type_, start):
    type_ = type_.lower()
    cls = {
        "daily": TimeOfDay,
        "weekly": DaysOfWeek,
        "hourly": TimeOfHour,
    }[type_]
    return cls(start, None)

def get_before(type_, end):
    type_ = type_.lower()
    cls = {
        "daily": TimeOfDay,
        "weekly": DaysOfWeek,
        "hourly": TimeOfHour,
    }[type_]
    return cls(None, end)

def get_full_cycle(type_):
    type_ = type_.lower()
    cls = {
        "daily": TimeOfDay,
        "weekly": DaysOfWeek,
        "hourly": TimeOfHour,
    }[type_]
    return cls(None, None)

# TODO: How to distinquise between the actual task and dependency? Modify the set_default_task

EXPRESSIONS = [
    # Another task ran as
    # TODO: These are always true after one run
    (r"after task '(?P<depend_task>.+)'",      DependSuccess),
    (r"after succeeded '(?P<depend_task>.+)'",        DependSuccess),
    (r"after finished '(?P<depend_task>.+)'",  DependFinish),
    (r"after failed '(?P<depend_task>.+)'",    DependFailure),
    
    (r"during running '(?P<task>.+)'",   TaskRunning), 
    # (r"after started '(?P<task>.+)'",   TaskStarted), # TODO

    # Run the task itself during specified 
    # (the task itself has not previously run during given period)
    (
        # TODO
        r"(run )?(?P<type_>monthly|weekly|daily|hourly|minutely) starting (?P<start>.+)", 
        lambda type_, start: TaskExecutable(period=get_starting(type_, start))
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
        lambda type_, start: TaskExecutable(period=get_before(type_, end))
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
        r"when time of (?P<type_>month|week|day|hour|minute) between (?P<start>.+) and (?P<end>.+)",
        lambda type_, start, end: IsPeriod(period=get_between(type_, start, end))
    ),
    (
        r"when time of (?P<type_>month|week|day|hour|minute) after (?P<start>.+)",
        lambda type_, start: IsPeriod(period=get_after(type_, start))
    ),
    (
        r"when time of (?P<type_>month|week|day|hour|minute) before (?P<end>.+)", 
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
