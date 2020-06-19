

from pathlib import Path
import subprocess

from pypipe.conditions.base import BaseCondition
from pypipe.conditions.event import task_ran
from pypipe.log import TaskAdapter, CsvHandler

from pypipe.conditions import AlwaysTrue, AlwaysFalse
from pypipe.time import period_factory
from pypipe import conditions
import logging
import inspect
import datetime

import pandas as pd

TASKS = {}

def get_task(task):
    return TASKS[task]

def _set_default_param(cond, task):
    if hasattr(cond, "event"):
        # is Occurrence condition
        event = cond.event
        if event.has_param("task") and not event.has_param_set("task"):
            cond.event.kwargs["task"] = task
        
def set_default_logger(filename="log/tasks.csv"):
    # Emptying existing handlers
    Task.logger.handlers = []

    # Making sure the log folder is found
    Path(filename).parent.mkdir(parents=True, exist_ok=True)

    # Adding the default handler
    handler = CsvHandler(
        filename,
        fields=[
            "asctime",
            "levelname",
            "action",
            "task_name",
            "exc_text",
        ]
    )
    Task.logger.addHandler(handler)

def set_queue_logger(queue):
    """Queue logging is required in case of multiprocessing
    Same log file cannot be written by multiple processes thus
    logging is carried away by a listener process"""
    # Emptying existing handlers
    Task.logger.handlers = []
    handler = logging.handlers.QueueHandler(queue)
    Task.logger.addHandler(handler)


class Task:
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

    # TODO:
    #   The force_run will not work with multiprocessing. The signal must be reseted with logging probably
    #   start_cond is a mess. Maybe different method to check the actual status of the Task? __bool__? Or add the depencency & execution conditions to the actual start_cond?


    logger = logging.getLogger(__name__)

    def __new__(cls, *args, **kwargs):
        "Store created tasks for easy acquisition"
        if not cls.logger.handlers:
            # Setting default handler 
            # as handler missing
            set_default_logger()

        instance = super().__new__(cls)
        task_name = kwargs.get("name", id(instance))

        if task_name in TASKS:
            raise KeyError(f"All tasks must have unique names. Given: {task_name}")

        TASKS[task_name] = instance
        return instance

    def __init__(self, action, 
                start_cond=None, run_cond=None, end_cond=None, 
                execution=None, dependent=None, timeout=None, priority=1, 
                on_success=None, on_failure=None, on_finish=None, 
                name=None):
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

        self.name = id(self) if name is None else name
        self.set_logger(self.logger)
        self._set_default_task()

        if self.status == "run":
            # Previously crashed unexpectedly during running
            # a new logging record is made to prevent leaving to
            # run status and releasing the task
            self.logger.warning(f'Task {self.name} previously crashed unexpectedly.', extra={"action": "crash_release"})

    def set_logger(self, logger):
        self.logger = TaskAdapter(logger, task=self)
    
    def _set_default_task(self):
        "Set the task in subconditions that are missing "
        for cond_set in (self.start_cond, self.run_cond, self.end_cond):
            if isinstance(cond_set, BaseCondition) and hasattr(cond_set, "apply"):
                cond_set.apply(_set_default_param, task=self)

    def __call__(self, *args, **params):
        self.log_running()
        #self.logger.info(f'Running {self.name}', extra={"action": "run"})
        
        try:
            params = self.filter_params(params)
            output = self.execute_action(*args, **params)

        except Exception as exception:
            status = "failed"
            self.log_failure()
            #self.logger.error(f'Task {self.name} failed', exc_info=True, extra={"action": "fail"})
            if self.on_failure:
                self.on_failure(exception=exception)
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
        
        return bool(self.start_cond & self._dependency_condition & self._execution_condition)
        

    def filter_params(self, params):
        sig = inspect.signature(self.action)
        required_params = [
            val
            for name, val in sig.parameters
            if val.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD, # Normal argument
                inspect.Parameter.KEYWORD_ONLY # Keyword argument
            )
        ]
        kwargs = {}
        for param in required_params:
            if param in params:
                kwargs[param] = params[param]
        return kwargs

    def log_running(self):
        self.logger.info(f"Running '{self.name}'", extra={"action": "run"})

    def log_failure(self):
        self.logger.error(f"Task '{self.name}' failed", exc_info=True, extra={"action": "fail"})

    def log_success(self):
        self.logger.info(f"Task '{self.name}' succeeded", extra={"action": "success"})

    def log_record(self, record):
        "For multiprocessing in which the record goes from copy of the task to scheduler before it comes back to the original task"
        self.logger.handle(record)

    def execute_action(self, *args, **kwargs):
        "Run the actual, given, task"
        return self.action(*args, **kwargs)

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

    @property
    def is_running(self):
        return self.status == "run"

    @property
    def status(self):
        record = self.logger.get_latest()
        if record is None:
            # No previous status
            return None
        return record["action"]

    @property
    def cycle(self):
        "Determine Time object for the interval (maximum possible if time independent as 'or')"
        execution = self._execution_condition
        if execution is not None:
            return execution.period 

    @property
    def execution(self):
        return self._execution

    @execution.setter
    def execution(self, value):
        self._execution = value

        if value is None:
            self._execution_condition = AlwaysTrue()
            return

        if isinstance(value, str):
            self._execution_condition = ~task_ran(task=self).in_cycle(value)
        else:
            # period is the execution variable
            cond = task_ran(task=self)
            cond.period = value
            self._execution_condition = ~cond

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

# Additional way to define execution
    def between(self, *args, **kwargs):
        execution = period_factory.between(*args, **kwargs)
        if self.execution is None:
            self.execution = execution
        else:
            self.execution &= execution
        return self

    def every(self, *args, **kwargs):
        execution = period_factory.past(*args, **kwargs)
        if self.execution is None:
            self.execution = execution
        else:
            self.execution &= execution
        return self

    def in_(self, *args, **kwargs):
        execution = period_factory.in_(*args, **kwargs)
        if self.execution is None:
            self.execution = execution
        else:
            self.execution &= execution
        return self

    def from_(self, *args, **kwargs):
        execution = period_factory.from_(*args, **kwargs)
        if self.execution is None:
            self.execution = execution
        else:
            self.execution &= execution
        return self

    def in_cycle(self, *args, **kwargs):
        execution = period_factory.in_cycle(*args, **kwargs)
        if self.execution is None:
            self.execution = execution
        else:
            self.execution &= execution
        return self


class ScriptTask(Task):

    main_func = "main"

    def execute_action(self, *args, **kwargs):

        script_path = self.action
        spec = importlib.util.spec_from_file_location("task", script_path)
        task_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(task_module)

        task_func = getattr(task_module, self.main_func)
        return task_func()


class CommandTask(Task):

    timeout = None

    def execute_action(self, *args, **kwargs):
        command = self.action
        if args:
            command = [command] + list(args) if isinstance(command, str) else command + list(args)

        pipe = subprocess.Popen(command,
                                shell=True,
                                #stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                )
        try:
            outs, errs = pipe.communicate(timeout=self.timeout)
        except TimeoutExpired:
            # https://docs.python.org/3.3/library/subprocess.html#subprocess.Popen.communicate
            pipe.kill()
            outs, errs = pipe.communicate()
            raise
        
        if pipe.returncode != 0:
            errs = errs.decode("utf-8", errors="ignore")
            raise OSError(f"Failed running command: \n{errs}")
        return stout


class JupyterTask(Task):

    def execute_action(self):
        nb = JupyterNotebook(self.action)

        if self.on_preprocess is not None:
            self.on_preprocess(nb)

        self._notebook = nb
        nb(inplace=True)

    def process_failure(self, exception):
        if self.on_failure:
            self.on_failure(self._notebook, exception=exception)
    
    def process_success(self, output):
        if self.on_success:
            self.on_success(self._notebook)

    def process_finish(self, status):
        if self.on_finish:
            self.on_finish(self._notebook, status)
        del self._notebook