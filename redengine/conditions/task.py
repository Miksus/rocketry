
import re, time
import datetime

from redengine.core.condition import Statement, Historical, Comparable
from redengine.core.time import TimeDelta
from .time import IsPeriod
from redengine.time.construct import get_before, get_between, get_full_cycle, get_after, get_on


class TaskStarted(Historical, Comparable):

    """Condition for whether a task has started
    (for given period).

    Examples
    --------

    **Parsing example:**

    >>> from redengine.parse import parse_condition
    >>> parse_condition("task 'mytask' has started today")
    TaskStarted(task='mytask', period=TimeOfDay(None, None))
    """

    def observe(self, task, _start_=None, _end_=None, **kwargs):

        task = Statement.session.get_task(task)
        if _start_ is None and _end_ is None:
            now = datetime.datetime.fromtimestamp(time.time())
            interv = task.period.rollback(now)
            _start_, _end_ = interv.left, interv.right

        allow_optimization = not self.session.config["force_status_from_logs"]
        if allow_optimization and self.any_over_zero():
            # Condition only checks whether has run at least once
            if task.last_run is None:
                return False
            elif _start_ <= task.last_run <= _end_:
                # Can probably be optimized only if inside the period (--> True)
                # else the old records must be fetched in case the task ran multiple times
                return True
        elif allow_optimization and self.equal_zero():
            return not bool(task.last_run)
        
        records = task.logger.get_records(timestamp=(_start_, _end_), action="run")
        run_times = [record["timestamp"] for record in records]
        return run_times
        
    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        period = self.period
        task = self.kwargs["task"]
        return f"task '{task}' started {period}"


class TaskFailed(Historical, Comparable):
    """Condition for whether the given task has failed
    (in given period).


    Examples
    --------

    **Parsing example:**

    >>> from redengine.parse import parse_condition
    >>> parse_condition("task 'mytask' has failed today between 10:00 and 14:00")
    TaskFailed(task='mytask', period=TimeOfDay('10:00', '14:00'))
    """

    def observe(self, task, _start_=None, _end_=None, **kwargs):
        task = Statement.session.get_task(task)
        if _start_ is None and _end_ is None:
            # If no period, start and end are the ones from the task
            now = datetime.datetime.fromtimestamp(time.time())
            interv = task.period.rollback(now)
            _start_, _end_ = interv.left, interv.right
        
        allow_optimization = not self.session.config["force_status_from_logs"]
        if allow_optimization and self.any_over_zero():
            # Condition only checks whether has run at least once
            if task.last_fail is None:
                return False
            elif _start_ <= task.last_fail <= _end_:
                # Can probably be optimized only if inside the period (--> True)
                # else the old records must be fetched in case the task ran multiple times
                return True
        elif allow_optimization and self.equal_zero():
            return not bool(task.last_fail)
        
        records = task.logger.get_records(timestamp=(_start_, _end_), action="fail")
        return [record["timestamp"] for record in records]

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        period = self.period
        task = self.kwargs["task"]
        return f"task '{task}' failed {period}"


class TaskTerminated(Historical, Comparable):
    """Condition for whether the given task has terminated
    (in given period).


    Examples
    --------
    
    **Parsing example:**

    >>> from redengine.parse import parse_condition
    >>> parse_condition("task 'mytask' has terminated this week after Monday")
    TaskTerminated(task='mytask', period=TimeOfWeek('Monday', None))
    """
    def observe(self, task, _start_=None, _end_=None, **kwargs):

        task = Statement.session.get_task(task)
        if _start_ is None and _end_ is None:
            # If no period, start and end are the ones from the task
            now = datetime.datetime.fromtimestamp(time.time())
            interv = task.period.rollback(now)
            _start_, _end_ = interv.left, interv.right
        
        allow_optimization = not self.session.config["force_status_from_logs"]
        if allow_optimization and self.any_over_zero():
            # Condition only checks whether has run at least once
            if task.last_terminate is None:
                return False
            elif _start_ <= task.last_terminate <= _end_:
                # Can probably be optimized only if inside the period (--> True)
                # else the old records must be fetched in case the task ran multiple times
                return True
        elif allow_optimization and self.equal_zero():
            return not bool(task.last_terminate)

        records = task.logger.get_records(timestamp=(_start_, _end_), action="terminate")
        return [record["timestamp"] for record in records]

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        period = self.period
        task = self.kwargs["task"]
        return f"task '{task}' terminated {period}"


class TaskSucceeded(Historical, Comparable):
    """Condition for whether the given task has succeeded
    (in given period).


    Examples
    --------
    
    **Parsing example:**

    >>> from redengine.parse import parse_condition
    >>> parse_condition("task 'mytask' has succeeded this month")
    TaskSucceeded(task='mytask', period=TimeOfMonth(None, None))
    """
    def observe(self, task, _start_=None, _end_=None, **kwargs):

        task = Statement.session.get_task(task)
        if _start_ is None and _end_ is None:
            now = datetime.datetime.fromtimestamp(time.time())
            interv = task.period.rollback(now)
            _start_, _end_ = interv.left, interv.right
        
        allow_optimization = not self.session.config["force_status_from_logs"]
        if allow_optimization and self.any_over_zero():
            # Condition only checks whether has run at least once
            if task.last_success is None:
                return False
            elif _start_ <= task.last_success <= _end_:
                # Can probably be optimized only if inside the period (--> True)
                # else the old records must be fetched in case the task ran multiple times
                return True
        elif allow_optimization and self.equal_zero():
            return not bool(task.last_success)

        records = task.logger.get_records(timestamp=(_start_, _end_), action="success")
        return [record["timestamp"] for record in records]

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        period = self.period
        task = self.kwargs["task"]
        return f"task 'task '{task}' succeeded {period}"


class TaskFinished(Historical, Comparable):
    """Condition for whether the given task has finished
    (in given period).


    Examples
    --------
    
    **Parsing example:**

    >>> from redengine.parse import parse_condition
    >>> parse_condition("task 'mytask' has finished today")
    TaskFinished(task='mytask', period=TimeOfDay(None, None))
    """
    def observe(self, task, _start_=None, _end_=None, **kwargs):

        task = Statement.session.get_task(task)
        if _start_ is None and _end_ is None:
            now = datetime.datetime.fromtimestamp(time.time())
            interv = task.period.rollback(now)
            _start_, _end_ = interv.left, interv.right

        allow_optimization = not self.session.config["force_status_from_logs"]
        if allow_optimization and self.any_over_zero():
            # Condition only checks whether has run at least once
            for status in ("success", "fail", "terminate"):
                value = getattr(task, f"last_{status}")
                if value is None:
                    continue
                if _start_ <= value <= _end_:
                    return True
            else:
                # Has never run
                return False
        elif allow_optimization and self.equal_zero():
            return not bool(task.last_success) and not bool(task.last_fail) and not bool(task.last_terminate)

        records = task.logger.get_records(timestamp=(_start_, _end_), action=["success", "fail", "terminate"])
        return [record["timestamp"] for record in records]

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        period = self.period
        task = self.kwargs["task"]
        return f"task '{task}' finished {period}"


class TaskRunning(Historical):

    """Condition for whether a task is currently
    running.

    Examples
    --------

    **Parsing example:**

    >>> from redengine.parse import parse_condition
    >>> parse_condition("task 'mytask' is running")
    TaskRunning(task='mytask')
    """
    #! TODO: Does this need to be Historical?

    __parsers__ = {
        re.compile(r"while task '(?P<task>.+)' is running"): "__init__",
        re.compile(r"task '(?P<task>.+)' is running"): "__init__",
    }

    def observe(self, task, **kwargs):

        task = Statement.session.get_task(task)

        if not self.session.config["force_status_from_logs"]:
            return bool(task.last_run)

        record = task.logger.get_latest()
        if not record:
            return False
        return record["action"] == "run"

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        task = self.kwargs["task"]
        return f"task '{task}' is running"


class TaskInacted(Historical, Comparable):
    """Condition for whether the given task has inacted
    (in given period).

    Examples
    --------

    **Parsing example:**

    >>> from redengine.parse import parse_condition
    >>> parse_condition("task 'mytask' has inacted")
    TaskInacted(task='mytask')
    """
    def observe(self, task, _start_=None, _end_=None, **kwargs):

        task = Statement.session.get_task(task)
        if _start_ is None and _end_ is None:
            # If no period, start and end are the ones from the task
            now = datetime.datetime.fromtimestamp(time.time())
            interv = task.period.rollback(now)
            _start_, _end_ = interv.left, interv.right
        
        allow_optimization = not self.session.config["force_status_from_logs"]
        if allow_optimization and self.any_over_zero():
            # Condition only checks whether has run at least once
            if task.last_inaction is None:
                return False
            return _start_ <= task.last_inaction <= _end_
        elif allow_optimization and self.equal_zero():
            return not bool(task.last_inaction)
        
        #! TODO: use Task._last_success & Task._last_run if not none and not forced
        records = task.logger.get_records(timestamp=(_start_, _end_), action="inaction")
        return [record["timestamp"] for record in records]

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        task = self.kwargs["task"]
        return f"task '{task}' inacted"


class TaskExecutable(Historical):
    """Condition for checking whether a given
    task has not finished (for given period).
    Useful to set the given task to run once 
    in given period.

    Examples
    --------

    **Parsing example:**

    >>> from redengine.parse import parse_condition
    >>> parse_condition("daily between 10:00 and 15:00")
    TaskExecutable(task=None, period=TimeOfDay('10:00', '15:00'))

    """

    def __init__(self, retries=None, task=None, period=None, **kwargs):
        if retries is not None:
            kwargs["retries"] = retries
        super().__init__(period=period, task=task, **kwargs)

        # TODO: If constant launching (allow launching alive tasks)
        # is to be implemented, there should be one more condition:
        # self._is_not_running

        # TODO: How to consider termination? Probably should be considered as failures without retries
        # NOTE: inaction is not considered at all

    def __bool__(self):
        period = self.period
        retries = self.kwargs.get("retries", 0)
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

    __parsers__ = {
        re.compile(r"(run )?(?P<type_>monthly|weekly|daily|hourly|minutely) (?P<span_type>starting) (?P<start>.+)"): "_from_period",
        re.compile(r"(run )?(?P<type_>monthly|weekly|daily|hourly|minutely) (?P<span_type>between) (?P<start>.+) and (?P<end>.+)"): "_from_period",
        re.compile(r"(run )?(?P<type_>monthly|weekly|daily|hourly|minutely) (?P<span_type>after) (?P<start>.+)"): "_from_period",
        re.compile(r"(run )?(?P<type_>monthly|weekly|daily|hourly|minutely) (?P<span_type>before) (?P<end>.+)"): "_from_period",
        re.compile(r"(run )?(?P<type_>monthly|weekly|daily|hourly|minutely)"): "_from_period",
        re.compile(r"(run )?(?P<type_>monthly|weekly|daily|hourly|minutely) (?P<span_type>on) (?P<start>.+)"): "_from_period",
        re.compile(r"(run )?(?P<span_type>every) (?P<past>.+)"): "_from_period",
    }


class DependFinish(Historical):
    """Condition for checking whether a given
    task has not finished after running a dependent 
    task. Useful to set the given task to run after
    another task has finished.

    Examples
    --------

    **Parsing example:**

    >>> from redengine.parse import parse_condition
    >>> parse_condition("after task 'other' finished")
    DependFinish(task=None, depend_task='other')
    """
    __parsers__ = {
        re.compile(r"after task '(?P<depend_task>.+)' finished"): "__init__",
    }
    def __init__(self, depend_task, task=None, **kwargs):
        super().__init__(task=task, depend_task=depend_task, **kwargs)

    def observe(self, task, depend_task, **kwargs):
        """True when the "depend_task" has finished and "task" has not yet ran after it.
        Useful for start cond for task that should be run after finish of another task.
        """
        # Name ideas: TaskNotRanAfterFinish, NotRanAfterFinish, DependFinish
        # HasRunAfterTaskFinished, RanAfterTask, RanAfterTaskFinished, AfterTaskFinished
        # TaskRanAfterFinish
        actual_task = Statement.session.get_task(task)
        depend_task = Statement.session.get_task(depend_task)

        #! TODO: use Task._last_success & Task._last_run if not none and not forced
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


class DependSuccess(Historical):
    """Condition for checking whether a given
    task has not succeeded after running a dependent 
    task. Useful to set the given task to run after
    another task has succeeded.

    Examples
    --------

    **Parsing example:**

    >>> from redengine.parse import parse_condition
    >>> parse_condition("after task 'other' succeeded")
    DependSuccess(task=None, depend_task='other')

    """

    __parsers__ = {
        re.compile(r"after task '(?P<depend_task>.+)'( succeeded)?"): "__init__",
    }

    def __init__(self, depend_task, task=None, **kwargs):
        super().__init__(task=task, depend_task=depend_task, **kwargs)

    def observe(self, task, depend_task, **kwargs):
        """True when the "depend_task" has succeeded and "task" has not yet ran after it.
        Useful for start cond for task that should be run after success of another task.
        """
        actual_task = Statement.session.get_task(task)
        depend_task = Statement.session.get_task(depend_task)

        #! TODO: use Task._last_success & Task._last_run if not none and not forced
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


class DependFailure(Historical):
    """Condition for checking whether a given
    task has not failed after running a dependent 
    task. Useful to set the given task to run after
    another task has failed.

    Examples
    --------

    **Parsing example:**

    >>> from redengine.parse import parse_condition
    >>> parse_condition("after task 'other' failed")
    DependFailure(task=None, depend_task='other')
    """

    __parsers__ = {
        re.compile(r"after task '(?P<depend_task>.+)' failed"): "__init__",
    }

    def __init__(self, depend_task, task=None, **kwargs):
        super().__init__(task=task, depend_task=depend_task, **kwargs)

    def observe(self, task, depend_task, **kwargs):
        """True when the "depend_task" has failed and "task" has not yet ran after it.
        Useful for start cond for task that should be run after failure of another task.
        """
        actual_task = Statement.session.get_task(task)
        depend_task = Statement.session.get_task(depend_task)

        #! TODO: use Task._last_success & Task._last_run if not none and not forced
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