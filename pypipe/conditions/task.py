
from pypipe.core.task import base
from pypipe.core.conditions import Statement, Historical, Comparable
from .time import IsPeriod

import psutil
import os
import datetime
import numpy as np


@Statement.from_func(historical=True, quantitative=True)
def TaskStarted(task, _start_=None, _end_=None, **kwargs):

    task = base.get_task(task)
    if _start_ is None and _end_ is None:
        now = datetime.datetime.now()
        interv = task.period.rollback(now)
        _start_, _end_ = interv.left, interv.right

    records = task.logger.get_records(start=_start_, end=_end_, action="run")
    run_times = records["asctime"].tolist()
    return run_times

@Statement.from_func(historical=True, quantitative=True)
def TaskFailed(task, _start_=None, _end_=None, **kwargs):

    task = base.get_task(task)
    if _start_ is None and _end_ is None:
        # If no period, start and end are the ones from the task
        now = datetime.datetime.now()
        interv = task.period.rollback(now)
        _start_, _end_ = interv.left, interv.right
    
    records = task.logger.get_records(start=_start_, end=_end_, action="fail")
    return records["asctime"].tolist()

@Statement.from_func(historical=True, quantitative=True)
def TaskSucceeded(task, _start_=None, _end_=None, **kwargs):

    task = base.get_task(task)
    if _start_ is None and _end_ is None:
        now = datetime.datetime.now()
        interv = task.period.rollback(now)
        _start_, _end_ = interv.left, interv.right
    
    records = task.logger.get_records(start=_start_, end=_end_, action="success")
    return records["asctime"].tolist()

@Statement.from_func(historical=True, quantitative=True)
def TaskFinished(task, _start_=None, _end_=None, **kwargs):

    task = base.get_task(task)
    if _start_ is None and _end_ is None:
        now = datetime.datetime.now()
        interv = task.period.rollback(now)
        _start_, _end_ = interv.left, interv.right

    records = task.logger.get_records(start=_start_, end=_end_, action=["success", "fail"])
    return records["asctime"].tolist()

@Statement.from_func(historical=False, quantitative=False)
def TaskRunning(task, **kwargs):

    task = base.get_task(task)

    record = task.logger.get_latest()
    if not record:
        return False
    return record["action"] == "run"


class TaskExecutable(Historical):
    """[summary]

    # Run only once between 10:00 and 14:00
    TaskExecutable(period=TimeOfDay("10:00", "14:00"))

    # Try twice (if fails) between 10:00 and 14:00
    TaskExecutable(period=TimeOfDay("10:00", "14:00"), retry=2)
    """
    def __init__(self, retries=0, task=None, period=None, **kwargs):

        self._has_not_succeeded = TaskSucceeded(period=period) == 0
        self._has_not_failed = TaskFailed(period=period) <= retries
        #self._has_retries = TaskFailed(period=None) <= retries # BUG: Now only allows to run if task has failed
        self._isin_period = IsPeriod(period=period)

        
        super().__init__(period=period, **kwargs)
        self.kwargs["retries"] = retries
        self.kwargs["task"] = task 
        #self._has_not_run = ~TaskFinished(period=self.period)

        # TODO: If constant launching (allow launching alive tasks)
        # is to be implemented, there should be one more condition:
        # self._is_not_running

    def __bool__(self):
        self._update_kwargs()
        return (
            bool(self._isin_period)
            and bool(self._has_not_succeeded) 
            and (bool(self._has_not_failed)) #  or bool(self._has_retries)
        )

    def _update_kwargs(self):
        self._has_not_succeeded.kwargs["task"] = self.kwargs["task"]
        self._has_not_failed.kwargs["task"] = self.kwargs["task"]

        self._has_not_failed.kwargs["_le_"] = self.kwargs["retries"]

    @property
    def period(self):
        return self._isin_period.period
    
    @period.setter
    def period(self, val):
        self._has_not_failed.period = val
        self._has_not_succeeded.period = val
        #self._has_retries.period = val
        self._isin_period.period = val


@Statement.from_func(historical=False, quantitative=False)
def DependFinish(task, depend_task, **kwargs):
    """True when the "depend_task" has finished and "task" has not yet ran after it.
    Useful for start cond for task that should be run after finish of another task.
    
    Illustration:
           task          depend_task      t0
            | -------------- | ------------
            >>> True

        depend_task         task          t0
            | -------------- | ------------
            >>> False

                                          t0
            -------------------------------
            >>> False
    """
    # Name ideas: TaskNotRanAfterFinish, NotRanAfterFinish, DependFinish
    # HasRunAfterTaskFinished, RanAfterTask, RanAfterTaskFinished, AfterTaskFinished
    # TaskRanAfterFinish
    actual_task = base.get_task(task)
    depend_task = base.get_task(depend_task)

    last_depend_finish = depend_task.logger.get_latest(action=["success", "fail"])
    last_actual_start = actual_task.logger.get_latest(action=["run"])

    if not last_depend_finish:
        # Depend has not run at all
        return False
    elif not last_actual_start:
        # Depend has finished but the actual task has not
        return True

    return last_depend_finish["asctime"] > last_actual_start["asctime"]

@Statement.from_func(historical=False, quantitative=False)
def DependSuccess(task, depend_task, **kwargs):
    """True when the "depend_task" has succeeded and "task" has not yet ran after it.
    Useful for start cond for task that should be run after success of another task.
    
    Illustration:
           task          depend_task      t0
            | -------------- | ------------
            >>> True

        depend_task         task          t0
            | -------------- | ------------
            >>> False

                                          t0
            -------------------------------
            >>> False
    """
    actual_task = base.get_task(task)
    depend_task = base.get_task(depend_task)

    last_depend_finish = depend_task.logger.get_latest(action=["success"])
    last_actual_start = actual_task.logger.get_latest(action=["run"])

    if not last_depend_finish:
        # Depend has not run at all
        return False
    elif not last_actual_start:
        # Depend has succeeded but the actual task has not
        return True
        
    return last_depend_finish["asctime"] > last_actual_start["asctime"]

@Statement.from_func(historical=False, quantitative=False)
def DependFailure(task, depend_task, **kwargs):
    """True when the "depend_task" has failed and "task" has not yet ran after it.
    Useful for start cond for task that should be run after failure of another task.
    
    Illustration:
           task          depend_task      t0
            | -------------- | ------------
            >>> True

        depend_task         task          t0
            | -------------- | ------------
            >>> False

                                          t0
            -------------------------------
            >>> False
    """
    actual_task = base.get_task(task)
    depend_task = base.get_task(depend_task)

    last_depend_finish = depend_task.logger.get_latest(action=["fail"])
    last_actual_start = actual_task.logger.get_latest(action=["run"])

    if not last_depend_finish:
        # Depend has not run at all
        return False
    elif not last_actual_start:
        # Depend has failed but the actual task has not
        return True
        
    return last_depend_finish["asctime"] > last_actual_start["asctime"]
