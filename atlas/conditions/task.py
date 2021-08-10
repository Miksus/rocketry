
from atlas.core.task import base
from atlas.core.conditions import Statement, Historical, Comparable
from atlas.core.time import TimeDelta
from .time import IsPeriod

import os
import datetime
import numpy as np

# TODO: instead of "Statement.session.get_task", use self.session

#@Statement.from_func(historical=True, quantitative=True, str_repr="task '{task}' stared {period}")
class TaskStarted(Historical, Comparable):

    def observe(self, task, _start_=None, _end_=None, **kwargs):

        task = Statement.session.get_task(task)
        if _start_ is None and _end_ is None:
            now = datetime.datetime.now()
            interv = task.period.rollback(now)
            _start_, _end_ = interv.left, interv.right

        records = task.logger.get_records(timestamp=(_start_, _end_), action="run")
        run_times = [record["timestamp"] for record in records]
        return run_times
        
    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        period = self.period
        task = self.kwargs["task"]
        return f"task '{task}' started {period}"

#@Statement.from_func(historical=True, quantitative=True, str_repr="task '{task}' failed {period}")
class TaskFailed(Historical, Comparable):

    def observe(self, task, _start_=None, _end_=None, **kwargs):
        task = Statement.session.get_task(task)
        if _start_ is None and _end_ is None:
            # If no period, start and end are the ones from the task
            now = datetime.datetime.now()
            interv = task.period.rollback(now)
            _start_, _end_ = interv.left, interv.right
        
        records = task.logger.get_records(timestamp=(_start_, _end_), action="fail")
        return [record["timestamp"] for record in records]

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        period = self.period
        task = self.kwargs["task"]
        return f"task '{task}' failed {period}"

#@Statement.from_func(historical=True, quantitative=True, str_repr="task '{task}' terminated {period}")
class TaskTerminated(Historical, Comparable):
    def observe(self, task, _start_=None, _end_=None, **kwargs):

        task = Statement.session.get_task(task)
        if _start_ is None and _end_ is None:
            # If no period, start and end are the ones from the task
            now = datetime.datetime.now()
            interv = task.period.rollback(now)
            _start_, _end_ = interv.left, interv.right
        
        records = task.logger.get_records(timestamp=(_start_, _end_), action="terminate")
        return [record["timestamp"] for record in records]

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        period = self.period
        task = self.kwargs["task"]
        return f"task '{task}' terminated {period}"

#@Statement.from_func(historical=True, quantitative=True, str_repr="task '{task}' succeeded {period}")
class TaskSucceeded(Historical, Comparable):
    def observe(self, task, _start_=None, _end_=None, **kwargs):

        task = Statement.session.get_task(task)
        if _start_ is None and _end_ is None:
            now = datetime.datetime.now()
            interv = task.period.rollback(now)
            _start_, _end_ = interv.left, interv.right
        
        records = task.logger.get_records(timestamp=(_start_, _end_), action="success")
        return [record["timestamp"] for record in records]

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        period = self.period
        task = self.kwargs["task"]
        return f"task 'task '{task}' succeeded {period}"

#@Statement.from_func(historical=True, quantitative=True, str_repr="task '{task}' finished {period}")
class TaskFinished(Historical, Comparable):
    def observe(self, task, _start_=None, _end_=None, **kwargs):

        task = Statement.session.get_task(task)
        if _start_ is None and _end_ is None:
            now = datetime.datetime.now()
            interv = task.period.rollback(now)
            _start_, _end_ = interv.left, interv.right

        records = task.logger.get_records(timestamp=(_start_, _end_), action=["success", "fail", "terminate"])
        return [record["timestamp"] for record in records]

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        period = self.period
        task = self.kwargs["task"]
        return f"task '{task}' finished {period}"

#@Statement.from_func(historical=False, quantitative=False, str_repr="task '{task}' is running")
class TaskRunning(Historical):
    def observe(self, task, **kwargs):

        task = Statement.session.get_task(task)

        record = task.logger.get_latest()
        if not record:
            return False
        return record["action"] == "run"

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        task = self.kwargs["task"]
        return f"task '{task}' is running"

#@Statement.from_func(historical=True, quantitative=True, str_repr="task '{task}' inacted")
class TaskInacted(Historical, Comparable):
    def observe(self, task, _start_=None, _end_=None, **kwargs):

        task = Statement.session.get_task(task)
        if _start_ is None and _end_ is None:
            # If no period, start and end are the ones from the task
            now = datetime.datetime.now()
            interv = task.period.rollback(now)
            _start_, _end_ = interv.left, interv.right
        
        records = task.logger.get_records(timestamp=(_start_, _end_), action="inaction")
        return [record["timestamp"] for record in records]

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        task = self.kwargs["task"]
        return f"task '{task}' inacted"

class TaskExecutable(Historical):
    """[summary]

    # Run only once between 10:00 and 14:00
    TaskExecutable(period=TimeOfDay("10:00", "14:00"))

    # Try twice (if fails) between 10:00 and 14:00
    TaskExecutable(period=TimeOfDay("10:00", "14:00"), retry=2)
    """
    def __init__(self, retries=0, task=None, period=None, **kwargs):
        
        super().__init__(period=period, retries=retries, task=task, **kwargs)

        # TODO: If constant launching (allow launching alive tasks)
        # is to be implemented, there should be one more condition:
        # self._is_not_running

        # TODO: How to consider termination? Probably should be considered as failures without retries
        # NOTE: inaction is not considered at all

    def __bool__(self):
        period = self.period
        retries = self.kwargs["retries"]
        task = self.kwargs["task"]

        # Form the sub statements
        has_not_succeeded = TaskSucceeded(period=period, task=task) == 0
        has_not_inacted = TaskInacted(period=period, task=task) == 0
        has_not_failed = TaskFailed(period=period, task=task) <= retries
        has_not_terminated = TaskTerminated(period=period, task=task) == 0

        isin_period = (
            # TimeDelta has no __contains__. One cannot say whether now is "past 2 hours".
            #   And please tell why this does not raise an exception then? - Future me
            True  
            if isinstance(period, TimeDelta) 
            else IsPeriod(period=period)
        )

        return (
            bool(isin_period)
            and bool(has_not_inacted)
            and bool(has_not_succeeded)
            and bool(has_not_failed)
            and bool(has_not_terminated)
        )

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        task = self.kwargs["task"]
        period = self.period
        return f"task '{task}' {self.period} "

#@Statement.from_func(historical=False, quantitative=False, str_repr="task '{depend_task}' finished before {task} started")
class DependFinish(Historical):
    def observe(self, task, depend_task, **kwargs):
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
        actual_task = Statement.session.get_task(task)
        depend_task = Statement.session.get_task(depend_task)

        last_depend_finish = depend_task.logger.get_latest(action=["success", "fail"])
        last_actual_start = actual_task.logger.get_latest(action=["run"])

        if not last_depend_finish:
            # Depend has not run at all
            return False
        elif not last_actual_start:
            # Depend has finished but the actual task has not
            return True

        return last_depend_finish["created"] > last_actual_start["created"]

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        task = self.kwargs["task"]
        depend_task = self.kwargs["depend_task"]
        return f"task '{depend_task}' finished before {task} started"


#@Statement.from_func(historical=False, quantitative=False, str_repr="task '{depend_task}' succeeded before {task} started")
class DependSuccess(Historical):
    def observe(self, task, depend_task, **kwargs):
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
        actual_task = Statement.session.get_task(task)
        depend_task = Statement.session.get_task(depend_task)

        last_depend_finish = depend_task.logger.get_latest(action=["success"])
        last_actual_start = actual_task.logger.get_latest(action=["run"])

        if not last_depend_finish:
            # Depend has not run at all
            return False
        elif not last_actual_start:
            # Depend has succeeded but the actual task has not
            return True
            
        return last_depend_finish["timestamp"] > last_actual_start["timestamp"]

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        task = self.kwargs["task"]
        depend_task = self.kwargs["depend_task"]
        return f"task '{depend_task}' finished before {task} started"

#@Statement.from_func(historical=False, quantitative=False, str_repr="task '{depend_task}' failed before {task} started")
class DependFailure(Historical):
    def observe(self, task, depend_task, **kwargs):
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
        actual_task = Statement.session.get_task(task)
        depend_task = Statement.session.get_task(depend_task)

        last_depend_finish = depend_task.logger.get_latest(action=["fail"])
        last_actual_start = actual_task.logger.get_latest(action=["run"])

        if not last_depend_finish:
            # Depend has not run at all
            return False
        elif not last_actual_start:
            # Depend has failed but the actual task has not
            return True
            
        return last_depend_finish["timestamp"] > last_actual_start["timestamp"]

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        task = self.kwargs["task"]
        depend_task = self.kwargs["depend_task"]
        return f"task '{depend_task}' finished before {task} started"