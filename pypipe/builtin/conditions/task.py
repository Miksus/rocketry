
from pypipe.core.task import base
from pypipe.core.conditions import Statement

import psutil
import os
import datetime
import numpy as np


@Statement.from_func(historical=True, quantitative=True)
def TaskStarted(task, _start_=None, _end_=None, **kwargs):
    # TODO: Rename as TaskStarted
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
