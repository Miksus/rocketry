import warnings
from rocketry.conditions import (
    DependFailure, DependFinish, DependSuccess, TaskFailed,
    TaskFinished, TaskRunnable,
    TaskStarted, TaskSucceeded,
    Retry,
    SchedulerStarted, SchedulerCycles,
)
from rocketry.conditions.func import FuncCond
from rocketry.core import (
    BaseCondition
)
from rocketry.core.condition import (
    AlwaysTrue, AlwaysFalse,
)
from rocketry.core.condition.base import All, Any
from rocketry.time import Cron

from rocketry.time import (
    TimeOfSecond, TimeOfMinute, TimeOfHour,
    TimeOfDay, TimeOfWeek, TimeOfMonth,
    TimeDelta, TimeSpanDelta
)

from .time import IsPeriod
from .task import TaskExecutable, TaskRunning

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
        period = self._cls_period.starting(start)
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

    def __str__(self):
        try:
            return BaseCondition.__str__(self)
        except AttributeError:
            return str(self.get_cond())

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

class RunningWrapper(BaseCondition):

    def __init__(self, task=None):
        self.task = task

    def observe(self, **kwargs):
        return self.get_cond().observe(**kwargs)

    def __call__(self, task=None, more_than=None, less_than=None):
        if more_than is not None or less_than is not None or task is None:
            warnings.warn(
                "running(more_than=..., less_than=...) and running() are derpecated. "
                "Please use running.more_than, running.less_than, running.between or just running instead.",
                DeprecationWarning
            )
            period = None
            if more_than is not None or less_than is not None:
                period = TimeSpanDelta(near=more_than, far=less_than, reference=self.session._get_datetime_now)
            return TaskRunning(task=task, period=period)
        return RunningWrapper(task)

    def more_than(self, delta):
        "Get condition the wrapper represents"
        period = TimeSpanDelta(near=delta, far=None, reference=self.session._get_datetime_now)
        return TaskRunning(task=self.task, period=period)

    def less_than(self, delta):
        "Get condition the wrapper represents"
        period = TimeSpanDelta(near=None, far=delta, reference=self.session._get_datetime_now)
        return TaskRunning(task=self.task, period=period)

    def between(self, more_than, less_than):
        "Get condition the wrapper represents"
        period = TimeSpanDelta(near=more_than, far=less_than, reference=self.session._get_datetime_now)
        return TaskRunning(task=self.task, period=period)

    def get_cond(self):
        "Get condition the wrapper represents"
        return TaskRunning(task=self.task)

    def __ge__(self, other):
        return self.get_cond() >= other

    def __le__(self, other):
        return self.get_cond() <= other

    def __gt__(self, other):
        return self.get_cond() > other

    def __lt__(self, other):
        return self.get_cond() < other

    def __eq__(self, other):
        return self.get_cond() == other

    def __ne__(self, other):
        return self.get_cond() != other

# Basics
# ------

true = AlwaysTrue()
false = AlwaysFalse()

# Execution related
# -----------------

secondly = TimeCondWrapper(TaskExecutable, TimeOfSecond)
minutely = TimeCondWrapper(TaskExecutable, TimeOfMinute)
hourly = TimeCondWrapper(TaskExecutable, TimeOfHour)
daily = TimeCondWrapper(TaskExecutable, TimeOfDay)
weekly = TimeCondWrapper(TaskExecutable, TimeOfWeek)
monthly = TimeCondWrapper(TaskExecutable, TimeOfMonth)

# Time related
# ------------

time_of_second = TimeCondWrapper(IsPeriod, TimeOfSecond)
time_of_minute = TimeCondWrapper(IsPeriod, TimeOfMinute)
time_of_hour = TimeCondWrapper(IsPeriod, TimeOfHour)
time_of_day = TimeCondWrapper(IsPeriod, TimeOfDay)
time_of_week = TimeCondWrapper(IsPeriod, TimeOfWeek)
time_of_month = TimeCondWrapper(IsPeriod, TimeOfMonth)

def every(past:str, based="run"):
    kws_past = {} # 'unit': 's'
    if based == "run":
        return TaskStarted(period=TimeDelta(past, kws_past=kws_past)) == 0
    if based == "success":
        return TaskSucceeded(period=TimeDelta(past, kws_past=kws_past)) == 0
    if based == "fail":
        return TaskFailed(period=TimeDelta(past, kws_past=kws_past)) == 0
    if based == "finish":
        return TaskExecutable(period=TimeDelta(past, kws_past=kws_past))
    raise ValueError(f"Invalid status: {based}")

def cron(__expr=None, **kwargs):
    if __expr:
        args = __expr.split(" ")
    else:
        args = ()

    period = Cron(*args, **kwargs)
    return TaskRunnable(period=period)

def crontime(__expr=None, **kwargs):
    if __expr:
        args = __expr.split(" ")
    else:
        args = ()

    period = Cron(*args, **kwargs)
    return IsPeriod(period=period)

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

running = RunningWrapper()

retry = RetryWrapper()

started = TimeActionWrapper(TaskStarted)
failed = TimeActionWrapper(TaskFailed)
succeeded = TimeActionWrapper(TaskSucceeded)
finished = TimeActionWrapper(TaskFinished)

# Scheduler
# ---------

def scheduler_running(more_than:str=None, less_than:str=None):
    return SchedulerStarted(period=TimeSpanDelta(near=more_than, far=less_than))

def scheduler_cycles(more_than:int=None, less_than:int=None):
    kwds = {}
    if more_than is not None:
        kwds['__gt__'] = more_than
    if less_than is not None:
        kwds['__lt__'] = less_than
    return SchedulerCycles.from_magic(**kwds)

# Custom
# ------

def condition():
    return FuncCond(syntax=None, decor_return_func=False)