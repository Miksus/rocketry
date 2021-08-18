
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

from .period_utils import (
    TIME_CLASSES,
    get_between,
    get_before,
    get_after,
    get_full_cycle
)

# Parsing declarations
for regex, func in [
    # Another task ran as
    (r"after '(?P<depend_task>.+)' succeeded", DependSuccess),
    (r"after '(?P<depend_task>.+)' finished",  DependFinish),
    (r"after '(?P<depend_task>.+)' failed",    DependFailure),
    (r"after '(?P<depend_task>.+)'",           DependSuccess),
    
    (r"while '(?P<task>.+)' is running",       TaskRunning), 
    (r"'(?P<task>.+)' is running",             TaskRunning), 
    (r"after '(?P<task>.+)' started",          TaskStarted),

    # Run the task itself during specified 
    # (the task itself has not previously run during given period)
    (r"(run )?(?P<type_>monthly|weekly|daily|hourly|minutely) starting (?P<start>.+)",                lambda **kwargs: TaskExecutable(period=get_full_cycle(**kwargs))),
    (r"(run )?(?P<type_>monthly|weekly|daily|hourly|minutely) between (?P<start>.+) and (?P<end>.+)", lambda **kwargs: TaskExecutable(period=get_between(**kwargs))),
    (r"(run )?(?P<type_>monthly|weekly|daily|hourly|minutely) after (?P<start>.+)",                   lambda **kwargs: TaskExecutable(period=get_after(**kwargs))),
    (r"(run )?(?P<type_>monthly|weekly|daily|hourly|minutely) before (?P<end>.+)",                    lambda **kwargs: TaskExecutable(period=get_before(**kwargs))),
    (r"(run )?(?P<type_>monthly|weekly|daily|hourly|minutely)",                                       lambda **kwargs: TaskExecutable(period=get_full_cycle(**kwargs))),
    (r"(run )?every (?P<past>.+)",                                                                   lambda **kwargs: TaskExecutable(period=TimeDelta(**kwargs))),

    # Time is as specified (TODO)
    (r"time of (?P<type_>month|week|day|hour|minute) between (?P<start>.+) and (?P<end>.+)", lambda **kwargs: IsPeriod(period=get_between(**kwargs))),
    (r"time of (?P<type_>month|week|day|hour|minute) after (?P<start>.+)",                   lambda **kwargs: IsPeriod(period=get_after(**kwargs))),
    (r"time of (?P<type_>month|week|day|hour|minute) before (?P<end>.+)",                    lambda **kwargs: IsPeriod(period=get_before(**kwargs))),

    (r"always true",  lambda: AlwaysTrue()),
    (r"always false", lambda: AlwaysFalse()),
    (r"true",         lambda: AlwaysTrue()),
    (r"false",        lambda: AlwaysFalse()),

    # Parameters
    (r"env '(?P<env>.+)'", IsEnv),
    # (r"parameter '(?P<key>.+)' is '(?P<value>.+)'", lambda: ParamExists())
    # (r"parameter '(?P<key>.+)' exists", lambda: ParamExists())

    # (r"(run )? weekend", lambda **kwargs: TaskExecutable(period=TimeOfWeek("Saturday", "Sunday"))),
    # TODO: 
        # "after 'depend_task' terminated"
        # ""
]:
    add_condition_parser(regex, func, regex=True)

# NOTE:
#   hourly/daily/weekly etc. is defined as starting from 0 of the interval instead of being time delta