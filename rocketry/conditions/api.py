from rocketry.conditions.task.task import DependFailure, DependFinish, DependSuccess
from rocketry.core import (
    BaseCondition
)
from rocketry.core.condition import (
    AlwaysTrue, AlwaysFalse,
)
from .time import IsPeriod
from .task import TaskExecutable
from rocketry.time import (
    TimeOfMinute, TimeOfHour,
    TimeOfDay, TimeOfWeek, TimeOfMonth,
    TimeDelta
)

class TimeCondWrapper(BaseCondition):

    def __init__(self, cls_cond, cls_period):
        self._cls_cond = cls_cond
        self._cls_period = cls_period

    def between(self, start, end):
        period = self._cls_period(start, end)
        return self._cls_cond(period=period)

    def before(self, end):
        period = self._cls_period(None, end)
        return self._cls_cond(period=period)

    def after(self, start):
        period = self._cls_period(start, None)
        return self._cls_cond(period=period)

    def on(self, span):
        period = self._cls_period(span, time_point=True)
        return self._cls_cond(period=period)

    def starting(self, start):
        period = self._cls_period(start, start)
        return self._cls_cond(period=period)

    def observe(self, **kwargs):
        period = self._cls_period(None, None)
        cond = self._cls_cond(period=period)
        return cond.observe(**kwargs)

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

def every(past:str):
    return TaskExecutable(period=TimeDelta(past))

# Task pipelining
# ---------------

def after_success(task):
    return DependSuccess(depend_task=task)

def after_fail(task):
    return DependFailure(depend_task=task)

def after_finish(task):
    return DependFinish(depend_task=task)
