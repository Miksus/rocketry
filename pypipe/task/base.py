from pypipe.conditions.base import BaseCondition
from pypipe.conditions import task_ran


from pypipe.conditions import AlwaysTrue, AlwaysFalse

from pypipe import conditions
from pypipe.conditions import set_statement_defaults
from .mixins import _ExecutionMixin, _LoggingMixin

import logging
import inspect

from functools import wraps

import pandas as pd

TASKS = {}

def get_task(task):
    return TASKS[task]

def clear_tasks():
    global TASKS
    TASKS = {}

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

        name {str} : Name of the task. Must be unique
        group {str} : Name of the group the task is part of. The name of the logger is derived using this.

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
    # TODO:
    #   The force_run will not work with multiprocessing. The signal must be reseted with logging probably
    #   start_cond is a mess. Maybe different method to check the actual status of the Task? __bool__? Or add the depencency & execution conditions to the actual start_cond?

    def __init__(self, action, 
                start_cond=None, run_cond=None, end_cond=None, 
                execution=None, dependent=None, timeout=None, priority=1, 
                on_success=None, on_failure=None, on_finish=None, 
                name=None, group=None):
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


        self.start_cond = AlwaysTrue() if start_cond is None else start_cond
        self.run_cond = AlwaysTrue() if run_cond is None else run_cond
        self.end_cond = AlwaysFalse() if end_cond is None else end_cond

        self.timeout = timeout
        self.priority = priority
        self.force_run = False

        self.on_failure = on_failure
        self.on_success = on_success
        self.on_finish = on_finish

        # Additional conditions
        self.execution = execution
        self.dependent = dependent

        self.group = group
        self.set_name(name)
        self.set_logger()
        self._set_default_task()

        if self.status == "run":
            # Previously crashed unexpectedly during running
            # a new logging record is made to prevent leaving to
            # run status and releasing the task
            self.logger.warning(f'Task {self.name} previously crashed unexpectedly.', extra={"action": "crash_release"})
        self._register_instance()

    def _set_default_task(self):
        "Set the task in subconditions that are missing "
        self.start_cond = set_statement_defaults(self.start_cond, task=self)
        self.run_cond = set_statement_defaults(self.run_cond, task=self)
        self.end_cond = set_statement_defaults(self.end_cond, task=self)

    def _register_instance(self):
        if self.name in TASKS:
            raise KeyError(f"All tasks must have unique names. Given: {self.name}. Already specified: {list(TASKS.keys())}")
        TASKS[self.name] = self

    def __call__(self, *args, **params):
        self.log_running()
        #self.logger.info(f'Running {self.name}', extra={"action": "run"})
        
        try:
            params = self.filter_params(params)
            output = self.execute_action(*args, **params)

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

    def __bool__(self):
        "Check whether the task can be run or not"
        if self.force_run:
            return True
        
        cond = bool(self.start_cond & self._dependency_condition & self._execution_condition)

        # There may be condition that set force_run True
        if self.force_run:
            return True
        return cond

    def filter_params(self, params):
        raise NotImplementedError(f"Parameter filter not implemented to {type(self)}")

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

    @property
    def dependent(self):
        return self._dependent

    @dependent.setter
    def dependent(self, value):
        self._dependent = value
        if value is None:
            self._dependency_condition = AlwaysTrue()
            return
        conds = [
            task_ran(get_task(task)).in_period(get_task(task).cycle)
            for task in value
        ]
        self._dependency_condition = conditions.All(conds)

    def set_name(self, name):
        if name is not None:
            self.name = name
        else:
            if self.use_instance_naming:
                self.name = id(self)
            else:
                self.name = self.get_default_name()

    def get_default_name(self):
        raise NotImplementedError(f"Method 'get_default_name' not implemented to {type(self)}")