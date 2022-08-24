from typing import Callable, Union
from rocketry.conditions import (
    DependFailure, DependFinish, DependSuccess, TaskFailed, 
    TaskFinished, TaskRunnable, 
    TaskStarted, TaskSucceeded,
    Retry,
    SchedulerStarted,
)
from rocketry.core import (
    BaseCondition
)
from rocketry.core.condition import (
    AlwaysTrue, AlwaysFalse,
)
from rocketry.core.condition.base import All, Any, Not
from rocketry.core.task import Task
from rocketry.time import Cron
from .time import IsPeriod
from .task import TaskExecutable, TaskRunning
from rocketry.time import (
    TimeOfMinute, TimeOfHour,
    TimeOfDay, TimeOfWeek, TimeOfMonth,
    TimeDelta, TimeSpanDelta
)

# Utility classes
# ---------------

class TimeCondWrapper(BaseCondition):

    def __init__(self, cls_cond, cls_period, **kwargs):
        self._cls_cond = cls_cond
        self._cls_period = cls_period
        self._cond_kwargs = kwargs

    def between(self, start, end):
        period = self._cls_period(start, end)
        return self._get_cond(period)

    def before(self, end):
        period = self._cls_period(None, end)
        return self._get_cond(period)

    def after(self, start):
        period = self._cls_period(start, None)
        return self._get_cond(period)

    def on(self, span):
        # Alias for "at"
        return self.at(span)

    def at(self, span):
        # Alias for "on"
        period = self._cls_period(span, time_point=True)
        return self._get_cond(period)

    def starting(self, start):
        period = self._cls_period(start, start)
        return self._get_cond(period)

    def observe(self, **kwargs):
        cond = self.get_cond()
        return cond.observe(**kwargs)

    def get_cond(self):
        "Get condition the wrapper itself represents"
        period = self._cls_period(None, None)
        return self._get_cond(period)

    def _get_cond(self, period):
        return self._cls_cond(period=period, **self._cond_kwargs)

class TimeActionWrapper(BaseCondition):

    def __init__(self, cls_cond, task=None):
        self.cls_cond = cls_cond
        self.task = task

    def observe(self, **kwargs):
        cond = self.get_cond()
        return cond.observe(**kwargs)

    def __call__(self, task):
        return TimeActionWrapper(self.cls_cond, task=task)

    @property
    def this_minute(self):
        return self._get_wrapper(TimeOfMinute)

    @property
    def this_hour(self):
        return self._get_wrapper(TimeOfHour)

    @property
    def this_day(self):
        return self._get_wrapper(TimeOfDay)

    @property
    def this_week(self):
        return self._get_wrapper(TimeOfWeek)

    @property
    def this_month(self):
        return self._get_wrapper(TimeOfMonth)

    @property
    def today(self):
        return self.this_day

    def _get_wrapper(self, cls_period):
        return TimeCondWrapper(cls_cond=self.cls_cond, cls_period=cls_period, task=self.task)

    def get_cond(self):
        "Get condition the wrapper represents"
        return self.cls_cond(task=self.task)

class RetryWrapper(BaseCondition):

    def __call__(self, n:int):
        return Retry(n)

    def observe(self, **kwargs):
        return self.get_cond().observe(**kwargs)

    def get_cond(self):
        "Get condition the wrapper represents"
        return Retry(-1)

# Basics
# ------

true = AlwaysTrue()
false = AlwaysFalse()

# Execution related
# -----------------

minutely = TimeCondWrapper(TaskExecutable, TimeOfMinute)
hourly = TimeCondWrapper(TaskExecutable, TimeOfHour)
daily = TimeCondWrapper(TaskExecutable, TimeOfDay)
weekly = TimeCondWrapper(TaskExecutable, TimeOfWeek)
monthly = TimeCondWrapper(TaskExecutable, TimeOfMonth)

# Time related
# ------------

time_of_minute = TimeCondWrapper(IsPeriod, TimeOfMinute)
time_of_hour = TimeCondWrapper(IsPeriod, TimeOfHour)
time_of_day = TimeCondWrapper(IsPeriod, TimeOfDay)
time_of_week = TimeCondWrapper(IsPeriod, TimeOfWeek)
time_of_month = TimeCondWrapper(IsPeriod, TimeOfMonth)

def every(past:str, based="run"):
    kws_past = {} # 'unit': 's'
    if based == "run":
        return TaskStarted(period=TimeDelta(past, kws_past=kws_past)) == 0
    elif based == "success":
        return TaskSucceeded(period=TimeDelta(past, kws_past=kws_past)) == 0
    elif based == "fail":
        return TaskFailed(period=TimeDelta(past, kws_past=kws_past)) == 0
    elif based == "finish":
        return TaskExecutable(period=TimeDelta(past, kws_past=kws_past))
    else:
        raise ValueError(f"Invalid status: {based}")

def cron(__expr=None, **kwargs):
    if __expr:
        args = __expr.split(" ")
    else:
        args = ()

    period = Cron(*args, **kwargs)
    return TaskRunnable(period=period)

# Task pipelining
# ---------------

def after_success(task):
    return DependSuccess(depend_task=task)

def after_fail(task):
    return DependFailure(depend_task=task)

def after_finish(task):
    return DependFinish(depend_task=task)


def after_all_success(*tasks):
    return All(*(after_success(task) for task in tasks))

def after_all_fail(*tasks):
    return All(*(after_fail(task) for task in tasks))

def after_all_finish(*tasks):
    return All(*(after_finish(task) for task in tasks))


def after_any_success(*tasks):
    return Any(*(after_success(task) for task in tasks))

def after_any_fail(*tasks):
    return Any(*(after_fail(task) for task in tasks))

def after_any_finish(*tasks):
    return Any(*(after_finish(task) for task in tasks))

# Task Status
# -----------

def running(more_than:str=None, less_than=None, task=None):
    if more_than is not None or less_than is not None:
        period = TimeSpanDelta(near=more_than, far=less_than)
    else:
        period = None
    return TaskRunning(task=task, period=period)

retry = RetryWrapper()

started = TimeActionWrapper(TaskStarted)
failed = TimeActionWrapper(TaskFailed)
succeeded = TimeActionWrapper(TaskSucceeded)
finished = TimeActionWrapper(TaskFinished)

# Scheduler
# ---------

def scheduler_running(more_than:str=None, less_than=None):
    return SchedulerStarted(period=TimeSpanDelta(near=more_than, far=less_than))
