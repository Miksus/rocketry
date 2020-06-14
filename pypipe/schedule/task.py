

from pathlib import Path
import subprocess

from pypipe.conditions.base import BaseCondition
from pypipe.conditions.event import task_ran
from pypipe.log import TaskAdapter, CsvHandler

from pypipe.conditions import AlwaysTrue, AlwaysFalse
from pypipe.time import period_factory
from pypipe import conditions
import logging


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
    """
    logger = logging.getLogger(__name__)

    def __new__(cls, *args, **kwargs):
        "Store created tasks for easy acquisition"
        if not cls.logger.handlers:
            # Setting default handler 
            # as handler missing
            print("Setting handlers")
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
        for cond_set in (self._start_cond, self.run_cond, self.end_cond):
            if isinstance(cond_set, BaseCondition) and hasattr(cond_set, "apply"):
                cond_set.apply(_set_default_param, task=self)

    def __call__(self, **params):
        self.log_running()
        #self.logger.info(f'Running {self.name}', extra={"action": "run"})
        try:
            output = self.execute_action(**params)

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

    def log_running(self):
        self.logger.info(f"Running '{self.name}'", extra={"action": "run"})

    def log_failure(self):
        self.logger.error(f"Task '{self.name}' failed", exc_info=True, extra={"action": "fail"})

    def log_success(self):
        self.logger.info(f"Task '{self.name}' succeeded", extra={"action": "success"})

    def execute_action(self, **kwargs):
        "Run the actual, given, task"
        return self.action(**kwargs)

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
    def start_cond(self):
        start_cond = self._start_cond
        if self.dependent is not None:
            start_cond &= self.dependency_condition

        if self.execution is not None:
            start_cond &= self.execution_condition

        return start_cond

    @start_cond.setter
    def start_cond(self, value):
        self._start_cond = value

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
        execution = self.execution_condition
        if execution is not None:
            return execution.condition.period 

    @property
    def execution_condition(self):
        execution = self.execution
        if execution is not None:
            if isinstance(execution, str):
                return ~task_ran(task=self).in_cycle(self.execution)
            else:
                # period is the execution variable
                cond = task_ran(task=self)
                cond.period = execution
                return ~cond

    @property
    def dependency_condition(self):
        if self.dependent is not None:
            return conditions.All([
                task_ran(get_task(task)).in_period(get_task(task).cycle)
                for task in self.dependent
            ])

# Additional way to define execution
    def between(self, *args, **kwargs):
        execution = period_factory.between(*args, **kwargs)
        if self.execution is None:
            self.execution = execution
        else:
            self.execution &= execution
        return self

    def past(self, *args, **kwargs):
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

    def execute_action(self):

        script_path = self.action
        spec = importlib.util.spec_from_file_location("task", script_path)
        task_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(task_module)

        task_func = getattr(task_module, self.main_func)
        return task_func()


class CommandlineTask(Task):

    def execute_action(self):
        command = self.action
        pipe = subprocess.Popen('dir',
                                shell=True,
                                #stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                )
        stout, stderr = pipe.communicate()
        
        if pipe.returncode != 0:
            stderr = stderr.decode("utf-8", errors="ignore")
            raise OSError("Failed running command: \n{stderr}")
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