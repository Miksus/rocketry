from typing import Callable, Union
from rocketry.conditions.task.task import DependFailure, DependFinish, DependSuccess
from rocketry.core import (
    BaseCondition
)
from rocketry.core.condition import (
    AlwaysTrue, AlwaysFalse,
)
from rocketry.core.condition.base import All, Any
from rocketry.core.task import Task
from .time import IsPeriod
from .task import TaskExecutable
from rocketry.time import (
    TimeOfMinute, TimeOfHour,
    TimeOfDay, TimeOfWeek, TimeOfMonth,
    TimeDelta
)

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