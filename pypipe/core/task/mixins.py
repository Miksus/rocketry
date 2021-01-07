
import datetime
import logging
from pathlib import Path

#from pypipe.core.conditions import TaskStarted
from pypipe.core.conditions import AlwaysTrue, AlwaysFalse
from pypipe.core.log import TaskAdapter

# TODO: This logger be set elsewhere than in core
from pypipe.log import CsvHandler

from pypipe.core.time import StaticInterval

class _ExecutionMixin:

    @property
    def execution(self):
        return self._execution

    @execution.setter
    def execution(self, value):
        self._execution = value

        if value is None:
            self._execution_condition = AlwaysTrue()
            return

        self._execution_condition = ~TaskStarted(task=self, period=value)

# Additional way to define execution
    def between(self, *args, **kwargs):
        execution = period_factory.between(*args, **kwargs)
        if self.execution is None:
            self.execution = execution
        else:
            # TODO
            self.execution &= execution
        return self

    def every(self, *args, **kwargs):
        execution = period_factory.past(*args, **kwargs)
        if self.execution is None:
            self.execution = execution
        else:
            # TODO
            self.execution &= execution
        return self

    def in_(self, *args, **kwargs):
        execution = period_factory.in_(*args, **kwargs)
        if self.execution is None:
            self.execution = execution
        else:
            # TODO
            self.execution &= execution
        return self

    def from_(self, *args, **kwargs):
        execution = period_factory.from_(*args, **kwargs)
        if self.execution is None:
            self.execution = execution
        else:
            # TODO
            self.execution &= execution
        return self

    def in_cycle(self, *args, **kwargs):
        execution = period_factory.in_cycle(*args, **kwargs)
        if self.execution is None:
            self.execution = execution
        else:
            # TODO
            self.execution &= execution
        return self

    @property
    def period(self):
        "Determine Time object for the interval (maximum possible if time independent as 'or')"
        execution = self._execution_condition
        if hasattr(execution, "period"):
            return execution.period 
        elif hasattr(execution, "__magicmethod__"):
            # TODO: What the fuck is this?
            return functools.reduce(lambda a, b : getattr(a, "__magicmethod__")(b), execution.subconditions)
        else:
            return StaticInterval()

    @property
    def next_start(self):
        "Next datetime when the task can be potentially run (more of a guess)"
        now = datetime.datetime.now()
        
        if bool(self._execution_condition):
            return now
        cond = self._execution_condition
        events = cond.function()
        latest_run = max(events)
        
        
        period = cond.period
        next_interval = period.next(latest_run) # Current interval
        return next_interval.left

class _LoggingMixin:

    default_logger = None

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, logger):
        if logger is None:
            # Get class logger (default logger)
            logger = type(self).default_logger

        if not logger.name.startswith(self._logger_basename):
            raise ValueError(f"Logger name must start with '{self._logger_basename}' as session finds loggers with names")

        if not isinstance(logger, TaskAdapter):
            logger = TaskAdapter(logger, task=self)
        self._logger = logger

    def log_running(self):
        self.logger.info(f"Running '{self.name}'", extra={"action": "run"})

    def log_failure(self):
        self.logger.error(f"Task '{self.name}' failed", exc_info=True, extra={"action": "fail"})

    def log_success(self):
        self.logger.info(f"Task '{self.name}' succeeded", extra={"action": "success"})

    def log_termination(self, reason=None):
        reason = reason or "unknown reason"
        self.logger.info(f"Task '{self.name}' terminated due to: {reason}", extra={"action": "terminate"})

    def log_record(self, record):
        "For multiprocessing in which the record goes from copy of the task to scheduler before it comes back to the original task"
        self.logger.handle(record)

    @property
    def status(self):
        record = self.logger.get_latest()
        if not record:
            # No previous status
            return None
        return record["action"]

    def get_history(self):
        records = self.logger.get_records()
        return records