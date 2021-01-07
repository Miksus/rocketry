
from pypipe.core.conditions import AlwaysTrue, AlwaysFalse, All
from pypipe.core.log import TaskAdapter
from pypipe.core.conditions import set_statement_defaults
from .mixins import _ExecutionMixin, _LoggingMixin


import logging
import inspect

from functools import wraps
from copy import copy

import pandas as pd

_TASKS = {}

def get_all_tasks():
    return _TASKS

def get_task(task):
    if isinstance(task, Task):
        return task
    return _TASKS[task]

def clear_tasks():
    global _TASKS
    _TASKS = {}

def reset_logger():
    Task.set_default_logger()

class Task(_ExecutionMixin, _LoggingMixin):
    """Executable task 

    This class is meant to be container
    for all the information needed to run
    the task

    Public attributes:
    ------------------
        action {function} : Function to execute as task. Parameters are passed by scheduler

        start_cond {Condition} : Condition to start the task (bool returns True)
        run_cond {Condition} : If condition returns False when task is running, termination occurs (only applicable with multiprocessing/threading)
        end_cond {Condition} : If condition returns True when task is running, termination occurs (only applicable with multiprocessing/threading)
        timeout {int, float} : Seconds allowed to run or terminated (only applicable with multiprocessing/threading)

        priority {int} : Priority of the task. Higher priority tasks are run first

        on_failure {function} : Function to execute if the action raises exception
        on_success {function} : Function to execute if the action succeessed
        on_finish {function} : Function to execute when the function finished (failed or success)

        execution {str, TimePeriod} : Time period when the task is allowed to run once and only once
            examples: "daily", "past 2 hours", "between 11:00 and 12:00"
        dependent {List[str]} : List of task names to must run before this task (in their execution cycle)

        name {str, tuple} : Name of the task. Must be unique
        groups {tuple} : Name of the group the task is part of. Different groups use different loggers

        force_run {bool} : Run the task manually once

    Readonly Properties:
    -----------
        is_running -> bool : Check whether the task is currently running or not
        status -> str : Latest status of the task

    Methods:
    --------
        __call__(*args, **kwargs) : Execute the task
        __bool__() : Whether the task can be run now or not
        filter_params(params:Dict) : Filter the passed parameters needed by the action

        between(*args, **kwargs) : Add execution condition of running the task between specified times
        past(*args, **kwargs) : Add execution condition of running the task in specified interval
        in_(*args, **kwargs) :

        log_running() : Log that the task is running
        log_failure() : Log that the task has failed
        log_success() : Log that the task has succeeded


    """
    use_instance_naming = False
    _logger_basename = __name__
    default_logger = logging.getLogger(_logger_basename)

    # TODO:
    #   The force_run will not work with multiprocessing. The signal must be reseted with logging probably
    #   start_cond is a mess. Maybe different method to check the actual status of the Task? __bool__? Or add the depencency & execution conditions to the actual start_cond?

    def __init__(self, action, 
                start_cond=None, run_cond=None, end_cond=None, 
                execution=None, dependent=None, timeout=None, priority=1, 
                on_success=None, on_failure=None, on_finish=None, 
                name=None, inputs=None, logger=None):
        """[summary]

        Arguments:
            condition {[type]} -- [description]
            action {[type]} -- [description]

        Keyword Arguments:
            priority {int} -- [description] (default: {1})
            on_success {[func]} -- Function to run on success (default: {None})
            on_failure {[func]} -- Function to run on failure (default: {None})
            on_finish {[func]} -- Function to run after running the task (default: {None})
        """
        self.action = action


        self.start_cond = AlwaysTrue() if start_cond is None else copy(start_cond)
        self.run_cond = AlwaysTrue() if run_cond is None else copy(run_cond)
        self.end_cond = AlwaysFalse() if end_cond is None else copy(end_cond)

        self.timeout = pd.Timedelta(timeout) if timeout is not None else timeout
        self.priority = priority
        self.force_run = False

        self.on_failure = on_failure
        self.on_success = on_success
        self.on_finish = on_finish

        # Additional conditions
        self.execution = execution
        if dependent is not None:
            self.set_dependent(dependent)

        #self.group = group
        self.name = name
        self.logger = logger
        self._set_default_task()

        if self.status == "run":
            # Previously crashed unexpectedly during running
            # a new logging record is made to prevent leaving to
            # run status and releasing the task
            self.logger.warning(f'Task {self.name} previously crashed unexpectedly.', extra={"action": "crash_release"})
        self._register_instance()

        # Whether the task is maintenance task
        self.is_maintenance = False

        # Input task
        self.inputs = [] if inputs is None else inputs

    def _set_default_task(self):
        "Set the task in subconditions that are missing "
        set_statement_defaults(self.start_cond, task=self)
        set_statement_defaults(self.run_cond, task=self)
        set_statement_defaults(self.end_cond, task=self)

    def _register_instance(self):
        if self.name in _TASKS:
            raise KeyError(f"All tasks must have unique names. Given: {self.name}. Already specified: {list(_TASKS.keys())}")
        _TASKS[self.name] = self

    def __call__(self, **params):
        self.log_running()
        #self.logger.info(f'Running {self.name}', extra={"action": "run"})
        
        try:
            params = self.filter_params(params)
            output = self.execute_action(params)

        except Exception as exception:
            status = "failed"
            self.log_failure()
            self.process_failure(exception=exception)
            #self.logger.error(f'Task {self.name} failed', exc_info=True, extra={"action": "fail"})

            self.exception = exception
            raise

        else:
            self.log_success()
            #self.logger.info(f'Task {self.name} succeeded', extra={"action": "success"})
            status = "succeeded"
            self.process_success(output)
            
            return output

        finally:
            self.process_finish(status=status)
            self.force_run = False

    def __bool__(self):
        "Check whether the task can be run or not"
        # TODO: rename force_run to forced_state that can be set to False (will not run any case) or True (will run once any case)
        # Also add methods: 
        #    set_pending() : Set forced_state to False
        #    resume() : Reset forced_state to None
        #    set_running() : Set forced_state to True

        if self.force_run:
            return True
        
        cond = bool(self.start_cond)

        # There may be condition that set force_run True
        if self.force_run:
            return True
        return cond

    def filter_params(self, params):
        return params

    def execute_action(self, *args, **kwargs):
        "Run the actual, given, task"
        raise NotImplementedError(f"Method 'execute_action' not implemented to {type(self)}")

    def process_failure(self, exception):
        if self.on_failure:
            self.on_failure(exception=exception)
    
    def process_success(self, output):
        if self.on_success:
            self.on_success(output)

    def process_finish(self, status):
        if self.on_finish:
            self.on_finish(status)

    @property
    def is_running(self):
        return self.status == "run"

    def set_execution(self, exec):
        # TODO: Remove?
        self.start_cond &= parse_statement(exec)

    def set_dependent(self, dependent:list):
        # TODO: Use DependSuccess
        self.start_cond &= All(TaskSucceeded(dep) for dep in dependent)

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        if name is None:
            name = (
                id(self)
                if self.use_instance_naming 
                else self.get_default_name()
            )
        self._name = str(name)

    def get_default_name(self):
        raise NotImplementedError(f"Method 'get_default_name' not implemented to {type(self)}")


# Logging
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

    def __getstate__(self):

        # capture what is normally pickled
        state = self.__dict__.copy()

        # remove unpicklable
        state['_logger'] = None
        # state['default_logger'] = None
        state['start_cond'] = None
        state['end_cond'] = None
        state['_execution_condition'] = None
        state['_dependency_condition'] = None
        state['_dependency_condition'] = None

        # what we return here will be stored in the pickle
        return state