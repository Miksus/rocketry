import re
from functools import partial

from rocketry.conditions.task import TaskFailed, TaskSucceeded, TaskFinished, TaskTerminated, TaskInacted, TaskStarted, TaskRunning, DependSuccess, DependFailure, DependFinish, get_on
from rocketry.conditions.scheduler import SchedulerStarted, SchedulerCycles
from rocketry.conditions.time import IsPeriod
from rocketry.conditions.parameter import ParamExists, IsEnv

from rocketry.time.construct import get_full_cycle, get_between, get_after, get_before
from rocketry.time import TimeDelta

from rocketry.session import Session
from rocketry.core.condition import Not

from rocketry.conds import (
    secondly, minutely, hourly, daily, weekly, monthly, every,
    cron
)

def _from_period_task_has(cls, span_type=None, inverse=False, **kwargs):

    period_func = {
        "between": get_between,
        "after": get_after,
        "before": get_before,
        "starting": get_full_cycle,
        None: get_full_cycle,
        "every": TimeDelta,
        "on": get_on,

        "past": TimeDelta,
    }[span_type]

    task = kwargs.pop("task", None)
    period = period_func(**kwargs)

    cls_kwargs = {"task": task} if task is not None else {}
    if inverse:
        return Not(cls(period=period, **cls_kwargs))
    return cls(period=period, **cls_kwargs)


def _set_is_period_parsing():

    def _get_is_period(period_constructor, *args, **kwargs):
        period = period_constructor(*args, **kwargs)
        return IsPeriod(period=period)

    cond_parsers = Session._cls_cond_parsers
    time_parsers = Session._time_parsers

    cond_parsers.update(
        {
            parsing: partial(_get_is_period, period_constructor=parser)
            for parsing, parser in time_parsers.items()
        }
    )

def _set_task_has_parsing():

    cond_parsers = Session._cls_cond_parsers

    clss = [
        ("failed", TaskFailed),
        ("succeeded", TaskSucceeded),
        ("finished", TaskFinished),
        ("terminated", TaskTerminated),
        ("inacted", TaskInacted),
        ("started", TaskStarted)
    ]
    for (action, cls) in clss:
        func = partial(_from_period_task_has, cls=cls)
        for prefix in ("", r"task '(?P<task>.+)' "):
            cond_parsers.update(
                {
                    re.compile(fr"{prefix}has {action}"): cls,
                    re.compile(fr"{prefix}has {action} (?P<type_>this month|this week|today|this hour|this minute) (?P<span_type>starting) (?P<start>.+)"): func,
                    re.compile(fr"{prefix}has {action} (?P<type_>this month|this week|today|this hour|this minute) (?P<span_type>between) (?P<start>.+) and (?P<end>.+)"): func,
                    re.compile(fr"{prefix}has {action} (?P<type_>this month|this week|today|this hour|this minute) (?P<span_type>after) (?P<start>.+)"): func,
                    re.compile(fr"{prefix}has {action} (?P<type_>this month|this week|today|this hour|this minute) (?P<span_type>before) (?P<end>.+)"): func,
                    re.compile(fr"{prefix}has {action} (?P<type_>this month|this week|today|this hour|this minute)"): func,
                    re.compile(fr"{prefix}has {action} (?P<type_>this month|this week|today|this hour|this minute) (?P<span_type>on) (?P<start>.+)"): func,
                    re.compile(fr"{prefix}has {action} (in )?past (?P<past>.+)"): partial(func, span_type='past'),
                }
            )

def _set_scheduler_parsing():

    cond_parsers = Session._cls_cond_parsers

    cls = SchedulerStarted
    func = partial(_from_period_task_has, cls=cls)
    cond_parsers.update(
        {
            re.compile(r"scheduler has run over (?P<past>.+)"): partial(func, span_type='past', inverse=True),
            re.compile(r"scheduler started (?P<past>.+) ago"): partial(func, span_type='past'),

            re.compile(r"scheduler has more than (?P<__gt__>[0-9]+) cycles"): SchedulerCycles.from_magic,
            re.compile(r"scheduler has less than (?P<__lt__>[0-9]+) cycles"): SchedulerCycles.from_magic,
            re.compile(r"scheduler has (?P<__eq__>[0-9]+) cycles"): SchedulerCycles.from_magic,
        }
    )

def _set_task_exec_parsing():
    cond_parsers = Session._cls_cond_parsers

    conds = {
        "secondly": secondly,
        "minutely": minutely,
        "hourly": hourly,
        "daily": daily,
        "weekly": weekly,
        "monthly": monthly,
    }
    options = {
        r' before (?P<end>.+)': 'before',
        r' between (?P<start>.+) and (?P<end>.+)': 'between',
        r' after (?P<start>.+)': 'after',
        r' starting (?P<start>.+)': 'starting',
        r' on (?P<span>.+)': 'on',
    }

    for str_period, cond in conds.items():
        cond_parsers[str_period] = cond

        for str_option, method_name in options.items():
            syntax = f"{str_period}{str_option}"
            method = getattr(cond, method_name)

            # Add to the syntax
            cond_parsers[re.compile(syntax)] = method
    # Add "every ..."
    cond_parsers[re.compile(r"every (?P<past>.+)")] = every

    # Cron
    cond_parsers[re.compile(r"cron (?P<__expr>.+)")] = cron

def _set_task_running_parsing():
    cond_parsers = Session._cls_cond_parsers

    cond_parsers.update(
        {
            re.compile(r"while task '(?P<task>.+)' is running"): TaskRunning,
            re.compile(r"task '(?P<task>.+)' is running"): TaskRunning,
        }
    )

def _set_task_pipelining_parsing():
    cond_parsers = Session._cls_cond_parsers

    cond_parsers.update(
        {
            re.compile(r"after task '(?P<depend_task>.+)'( succeeded)?"): DependSuccess,
            re.compile(r"after tasks '(?P<depend_tasks>.+)'( succeeded)?"): DependSuccess._parse_multi_all,
            re.compile(r"after any tasks '(?P<depend_tasks>.+)'( succeeded)?"): DependSuccess._parse_multi_any,

            re.compile(r"after task '(?P<depend_task>.+)' failed"): DependFailure,
            re.compile(r"after tasks '(?P<depend_tasks>.+)' failed"): DependFailure._parse_multi_all,
            re.compile(r"after any tasks '(?P<depend_tasks>.+)' failed"): DependFailure._parse_multi_any,

            re.compile(r"after task '(?P<depend_task>.+)' finished"): DependFinish,
            re.compile(r"after tasks '(?P<depend_tasks>.+)' finished"): DependFinish._parse_multi_all,
            re.compile(r"after any tasks '(?P<depend_tasks>.+)' finished"): DependFinish._parse_multi_any,
        }
    )

def _set_misc_parsing():
    cond_parsers = Session._cls_cond_parsers

    cond_parsers.update(
        {
            re.compile(r"env '(?P<env>.+)'"): IsEnv,
            re.compile(r"param '(?P<l>.+)' exists"): ParamExists._from_list,
            re.compile(r"param '(?P<key>.+)' is '(?P<value>.+)'"): ParamExists._from_key_value,
        }
    )

_set_is_period_parsing()
_set_task_has_parsing()
_set_scheduler_parsing()
_set_task_exec_parsing()

_set_task_running_parsing()
_set_task_pipelining_parsing()
_set_misc_parsing()
