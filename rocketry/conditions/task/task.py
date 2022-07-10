
import re, time
import datetime
from typing import Tuple
from rocketry.core import task
from rocketry.core.condition import BaseCondition

from rocketry.core.time import TimePeriod
from rocketry.core.time.utils import get_period_span, to_timestamp
from .utils import DependMixin, TaskStatusMixin

from redbird.oper import between

from rocketry.core.condition import Statement, Historical, BaseComparable, All
from rocketry.core.time import TimeDelta
from ..time import IsPeriod
from rocketry.time.construct import get_before, get_between, get_full_cycle, get_after, get_on
from rocketry.args import Task, Session
from rocketry.log.utils import get_field_value

class TaskStarted(BaseComparable):

    """Condition for whether a task has started
    (for given period).

    Examples
    --------

    **Parsing example:**

    >>> from rocketry.parse import parse_condition
    >>> parse_condition("task 'mytask' has started today")
    TaskStarted(task='mytask', period=TimeOfDay(None, None))
    """

    def __init__(self, task=None, period=None):
        self.task = task
        self.period = period
        super().__init__()

    def get_measurement(self, task=Task(), session=Session()):
        task = task if self.task is None else session[self.task]
        _start_, _end_ = get_period_span(self.period if self.period is not None else task.period)

        allow_optimization = not self.session.config.force_status_from_logs
        if allow_optimization and self._is_any_over_zero():
            # Condition only checks whether has run at least once
            if task.last_run is None:
                return False
            elif _start_ <= task.last_run <= _end_:
                # Can probably be optimized only if inside the period (--> True)
                # else the old records must be fetched in case the task ran multiple times
                return True
        elif allow_optimization and self._is_equal_zero():
            return not bool(task.last_run)
        
        records = task.logger.get_records(created=between(to_timestamp(_start_), to_timestamp(_end_)), action="run")
        run_times = [get_field_value(record, "created") for record in records]
        return len(run_times)
        
    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        period = self.period
        task = self.task
        task_name = getattr(task, 'name', str(task))
        period = '' if period is None else f' {period}'
        return f"task '{task_name}' started{period}"


class TaskFailed(TaskStatusMixin):
    """Condition for whether the given task has failed
    (in given period).


    Examples
    --------

    **Parsing example:**

    >>> from rocketry.parse import parse_condition
    >>> parse_condition("task 'mytask' has failed today between 10:00 and 14:00")
    TaskFailed(task='mytask', period=TimeOfDay('10:00', '14:00'))
    """
    _action = 'fail'

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        period = self.period
        task = self.task
        task_name = getattr(task, 'name', str(task))
        period = '' if period is None else f' {period}'
        return f"task '{task_name}' failed{period}"


class TaskTerminated(TaskStatusMixin):
    """Condition for whether the given task has terminated
    (in given period).


    Examples
    --------
    
    **Parsing example:**

    >>> from rocketry.parse import parse_condition
    >>> parse_condition("task 'mytask' has terminated this week after Monday")
    TaskTerminated(task='mytask', period=TimeOfWeek('Monday', None))
    """
    _action = 'terminate'
    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        period = self.period
        task = self.task
        task_name = getattr(task, 'name', str(task))
        period = '' if period is None else f' {period}'
        return f"task '{task_name}' terminated{period}"


class TaskSucceeded(TaskStatusMixin):
    """Condition for whether the given task has succeeded
    (in given period).


    Examples
    --------
    
    **Parsing example:**

    >>> from rocketry.parse import parse_condition
    >>> parse_condition("task 'mytask' has succeeded this month")
    TaskSucceeded(task='mytask', period=TimeOfMonth(None, None))
    """
    _action = 'success'

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        period = self.period
        task = self.task
        task_name = getattr(task, 'name', str(task))
        period = '' if period is None else f' {period}'
        return f"task '{task_name}' succeeded{period}"


class TaskFinished(TaskStatusMixin):
    """Condition for whether the given task has finished
    (in given period).


    Examples
    --------
    
    **Parsing example:**

    >>> from rocketry.parse import parse_condition
    >>> parse_condition("task 'mytask' has finished today")
    TaskFinished(task='mytask', period=TimeOfDay(None, None))
    """
    _action = ["success", "fail", "terminate"]

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        period = self.period
        task = self.task
        task_name = getattr(task, 'name', str(task))
        period = '' if period is None else f' {period}'
        return f"task '{task_name}' finished" + period


class TaskRunning(BaseCondition):

    """Condition for whether a task is currently
    running.

    Examples
    --------

    **Parsing example:**

    >>> from rocketry.parse import parse_condition
    >>> parse_condition("task 'mytask' is running")
    TaskRunning(task='mytask')
    """
    #! TODO: Does this need to be Historical?

    __parsers__ = {
        re.compile(r"while task '(?P<task>.+)' is running"): "__init__",
        re.compile(r"task '(?P<task>.+)' is running"): "__init__",
    }

    def __init__(self, task=None):
        self.task = task
        super().__init__()

    def get_state(self, task=Task(), session=Session()):
        task = session[self.task] if self.task is not None else task
        
        if not self.session.config.force_status_from_logs:
            return bool(task.last_run)

        record = task.logger.get_latest()
        if not record:
            return False
        return record.action == "run"

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        task = self.task
        task_name = getattr(task, 'name', str(task))
        return f"task '{task_name}' is running"


class TaskInacted(TaskStatusMixin):
    """Condition for whether the given task has inacted
    (in given period).

    Examples
    --------

    **Parsing example:**

    >>> from rocketry.parse import parse_condition
    >>> parse_condition("task 'mytask' has inacted")
    TaskInacted(task='mytask')
    """
    _action = 'inaction'

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        task = self.task
        task_name = getattr(task, 'name', str(task))
        return f"task '{task_name}' inacted"


class TaskExecutable(BaseCondition):
    """Condition for checking whether a given
    task has not finished (for given period).
    Useful to set the given task to run once 
    in given period.

    Examples
    --------

    **Parsing example:**

    >>> from rocketry.parse import parse_condition
    >>> parse_condition("daily between 10:00 and 15:00")
    TaskExecutable(task=None, period=TimeOfDay('10:00', '15:00'))

    """

    def __init__(self, retries=None, task=None, period=None):
        self.retries = retries
        self.period = period
        self.task = task
        super().__init__()

        # TODO: If constant launching (allow launching alive tasks)
        # is to be implemented, there should be one more condition:
        # self._is_not_running

        # TODO: How to consider termination? Probably should be considered as failures without retries
        # NOTE: inaction is not considered at all

    def get_state(self, task=Task(), session=Session()):
        task = self.task if self.task is not None else task
        period = self.period
        retries = 0 if self.retries is None else self.retries

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
            isin_period.observe()
            and has_not_inacted.observe(task=task, session=session)
            and has_not_succeeded.observe(task=task, session=session)
            and has_not_failed.observe(task=task, session=session)
            and has_not_terminated.observe(task=task, session=session)
        )

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        task = self.task
        period = self.period
        return f"task '{task}' {self.period}"

    @classmethod
    def _from_period(cls, span_type=None, **kwargs):
        period_func = {
            "between": get_between,
            "after": get_after,
            "before": get_before,
            "starting": get_full_cycle,
            None: get_full_cycle,
            "every": TimeDelta,
            "on": get_on,
        }[span_type]
        period = period_func(**kwargs)
        return cls(period=period)


class DependFinish(DependMixin):
    """Condition for checking whether a given
    task has not finished after running a dependent 
    task. Useful to set the given task to run after
    another task has finished.

    Examples
    --------

    **Parsing example:**

    >>> from rocketry.parse import parse_condition
    >>> parse_condition("after task 'other' finished")
    DependFinish(task=None, depend_task='other')
    """
    __parsers__ = {
        re.compile(r"after task '(?P<depend_task>.+)' finished"): "__init__",
        re.compile(r"after tasks '(?P<depend_tasks>.+)' finished"): "_parse_multi_all",
        re.compile(r"after any tasks '(?P<depend_tasks>.+)' finished"): "_parse_multi_any",
    }
    _dep_actions = ['success', 'fail']

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        task = self.task
        depend_task = self.depend_task
        task_name = getattr(task, 'name', str(task))
        depend_task_name = getattr(depend_task, 'name', str(depend_task))
        return f"task '{depend_task_name}' finished before '{task_name}' started"


class DependSuccess(DependMixin):
    """Condition for checking whether a given
    task has not succeeded after running a dependent 
    task. Useful to set the given task to run after
    another task has succeeded.

    Examples
    --------

    **Parsing example:**

    >>> from rocketry.parse import parse_condition
    >>> parse_condition("after task 'other' succeeded")
    DependSuccess(task=None, depend_task='other')

    """

    __parsers__ = {
        re.compile(r"after task '(?P<depend_task>.+)'( succeeded)?"): "__init__",
        re.compile(r"after tasks '(?P<depend_tasks>.+)'( succeeded)?"): "_parse_multi_all",
        re.compile(r"after any tasks '(?P<depend_tasks>.+)'( succeeded)?"): "_parse_multi_any",
    }
    _dep_actions = ['success']

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        task = self.task
        depend_task = self.depend_task
        task_name = getattr(task, 'name', str(task))
        depend_task_name = getattr(depend_task, 'name', str(depend_task))
        return f"task '{depend_task_name}' succeeded before '{task_name}' started"


class DependFailure(DependMixin):
    """Condition for checking whether a given
    task has not failed after running a dependent 
    task. Useful to set the given task to run after
    another task has failed.

    Examples
    --------

    **Parsing example:**

    >>> from rocketry.parse import parse_condition
    >>> parse_condition("after task 'other' failed")
    DependFailure(task=None, depend_task='other')
    """

    __parsers__ = {
        re.compile(r"after task '(?P<depend_task>.+)' failed"): "__init__",
        re.compile(r"after tasks '(?P<depend_tasks>.+)' failed"): "_parse_multi_all",
        re.compile(r"after any tasks '(?P<depend_tasks>.+)' failed"): "_parse_multi_any",
    }
    _dep_actions = ['fail']

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        task = self.task
        depend_task = self.depend_task
        task_name = getattr(task, 'name', str(task))
        depend_task_name = getattr(depend_task, 'name', str(depend_task))
        return f"task '{depend_task_name}' failed before '{task_name}' started"