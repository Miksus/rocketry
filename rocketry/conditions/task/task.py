from typing import Optional
import datetime

from redbird.oper import in_, greater_equal, between

from rocketry.core.condition import BaseCondition, BaseComparable
from rocketry.log.utils import get_field_value
from rocketry.pybox.time import to_timestamp
from rocketry.time.construct import get_before, get_between, get_full_cycle, get_after, get_on
from rocketry.args import Task, Session
from rocketry.core.time.utils import get_period_span
from rocketry.core.time import TimeDelta
from .utils import DependMixin, TaskStatusMixin

from ..time import IsPeriod


class TaskStarted(TaskStatusMixin):

    """Condition for whether a task has started
    (for given period).

    Examples
    --------

    **Parsing example:**

    >>> from rocketry.parse import parse_condition
    >>> parse_condition("task 'mytask' has started today")
    TaskStarted(task='mytask', period=TimeOfDay(None, None))
    """
    _action = 'run'

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


class TaskRunning(BaseComparable):

    """Condition for whether a task is currently
    running.

    Examples
    --------

    **Parsing example:**

    >>> from rocketry.parse import parse_condition
    >>> parse_condition("task 'mytask' is running")
    TaskRunning(task='mytask')
    """

    def __init__(self, task=None, period:TimeDelta=None):
        self.task = task
        self.period = period
        super().__init__()

    def get_measurement(self, task=Task(default=None), session=Session()):
        task = session[self.task] if self.task is not None else task

        allow_optimization = not self.session.config.force_status_from_logs
        start, end = get_period_span(self.period, session=session)
        if allow_optimization:
            task = session[self.task] if self.task is not None else task
            runs = [
                run.start
                for run in task._run_stack
                if run.is_alive() and start <= session._format_timestamp(run.start) <= end
            ]
            return runs

        records = task.logger.get_records(
            created=between(to_timestamp(start), to_timestamp(end)),
        )
        records = sorted(records, key=lambda x: get_field_value(x, "created"))
        runs = []
        has_run_id = True
        try:
            finishes = [
                get_field_value(record, "run_id")
                for record in records
                if get_field_value(record, "run_id") and get_field_value(record, "action") != "run"
            ]
        except (KeyError, AttributeError):
            # Logs have no run_id
            finishes = [
                get_field_value(record, "created")
                for record in records
                if get_field_value(record, "action") != "run"
            ]
            has_run_id = False

        for record in records:
            action = get_field_value(record, "action")
            is_run = action == "run"
            if not is_run:
                continue
            if has_run_id:
                run_id = get_field_value(record, "run_id")
                if run_id not in finishes:
                    runs.append(run_id)
            else:
                # Less optimized, tries to guess which is the finish
                created = get_field_value(record, "created")
                for finish in finishes.copy():
                    if finish >= created:
                        # match
                        finishes.remove(finish)
                        break
                else:
                    # No finishes
                    runs.append(created)
        return runs

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

    def get_state(self, task=Task(default=None), session=Session()):
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
            #   Because the period is used in the sub statements and TimeDelta is still accepted - Senior me
            True
            if isinstance(period, TimeDelta)
            else IsPeriod(period=period).observe(session=session)
        )

        return (
            isin_period
            and has_not_inacted.observe(task=task, session=session)
            and has_not_succeeded.observe(task=task, session=session)
            and has_not_failed.observe(task=task, session=session)
            and has_not_terminated.observe(task=task, session=session)
        )

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        task = self.task
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


class TaskRunnable(BaseCondition):
    """Condition for checking whether a given
    task has not run (for given period).
    Useful to set the given task to run once
    in given period.
    """

    def __init__(self, task=None, period=None):
        self.period = period
        self.task = task
        super().__init__()

    def get_state(self, task=Task(default=None), session=Session()):
        task = self.task if self.task is not None else task
        period = self.period

        has_not_run = TaskStarted(period=period, task=task) == 0

        isin_period = (
            True
            if isinstance(period, TimeDelta)
            else IsPeriod(period=period).observe(session=session)
        )

        return (
            isin_period
            and has_not_run.observe(task=task, session=session)
        )

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        period = self.period
        task = self.task
        task_name = getattr(task, "name", str(task))
        period = "" if period is None else f" {period}"
        return f"task '{task_name}' runnable{period}"


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

    _dep_actions = ['fail']

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        task = self.task
        depend_task = self.depend_task
        task_name = getattr(task, 'name', str(task))
        depend_task_name = getattr(depend_task, 'name', str(depend_task))
        return f"task '{depend_task_name}' failed before '{task_name}' started"

class Retry(BaseCondition):
    """Condition for retrying failed attempts"""
    def __init__(self, n: Optional[int] = 1):
        self.n = int(n) if n is not None else -1
        super().__init__()

    def get_state(self, task=Task(default=None), session=Session()):
        if self.n == 0:
            return False
        if task.get_status() != "fail":
            # Previously did not fail, no need to retry
            return False
        if self.n == -1:
            # Infinite retries
            return True

        last_non_fail = task.logger.filter_by(
            action=in_(['success', 'crash', 'inaction', 'terminate'])
        ).last()

        last_non_fail_created = 0 if last_non_fail is None else last_non_fail.created

        n_failed_in_row = task.logger.filter_by(
            created=greater_equal(last_non_fail_created),
            action='fail'
        ).count()
        return self.n >= n_failed_in_row
