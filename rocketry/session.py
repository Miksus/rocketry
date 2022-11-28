"""
Utilities for getting information
about the scehuler/task/parameters etc.
"""

from copy import copy
import datetime
import logging
from multiprocessing import cpu_count
import time
import threading
import warnings

from itertools import chain
from typing import TYPE_CHECKING, Callable, ClassVar, Iterable, Dict, List, Optional, Set, Tuple, Type, Union
from pydantic import BaseModel, root_validator, validator
from rocketry.pybox.time import to_timedelta
from rocketry.log.defaults import create_default_handler
from rocketry._base import RedBase
from rocketry.tasks.run_id import uuid

try:
    from typing import Literal
except ImportError: # pragma: no cover
    from typing_extensions import Literal


if TYPE_CHECKING:
    from rocketry.core.log import TaskAdapter
    from rocketry.parse import StaticParser
    from rocketry.core import (
        Task,
        Scheduler,
        BaseCondition,
        Parameters,
        BaseArgument,
        TimePeriod
    )



class Config(BaseModel):
    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True

    # Fields
    use_instance_naming: bool = False
    task_priority: int = 0
    execution: Optional[str] = None
    task_pre_exist: str = 'raise'
    force_status_from_logs: bool = False # Force to check status from logs every time (slow but robust)

    task_logger_basename: str = "rocketry.task"
    scheduler_logger_basename: str = "rocketry.scheduler"

    silence_task_prerun: bool = False # Whether to silence errors occurred in setting a task to run
    silence_task_logging: bool = False # Whether to silence errors occurred in logging a task
    silence_cond_check: bool = False # Whether to silence errors occurred in checking conditions
    cycle_sleep: Optional[float] = 0.1
    debug: bool = False

    multilaunch: bool = False
    func_run_id: Callable = uuid
    max_process_count = cpu_count()
    tasks_as_daemon: bool = True
    restarting: str = 'replace'
    instant_shutdown: bool = False

    timeout: datetime.timedelta = datetime.timedelta(minutes=30)
    shut_cond: Optional['BaseCondition'] = None
    cls_lock: Type = threading.Lock

    param_materialize:Literal['pre', 'post'] = 'post'

    timezone: Optional[datetime.tzinfo] = None
    time_func: Callable = None

    @validator('execution', pre=True, always=True)
    def parse_task_execution(cls, value):
        if value is None:
            return 'async'
        return value

    @validator('shut_cond', pre=True)
    def parse_shut_cond(cls, value):
        from rocketry.parse import parse_condition
        from rocketry.conditions import AlwaysFalse
        if value is None:
            return AlwaysFalse()
        return parse_condition(value)

    @validator('timeout', pre=True, always=True)
    def parse_timeout(cls, value):
        if isinstance(value, str):
            return to_timedelta(value)
        if isinstance(value, (float, int)):
            return datetime.timedelta(seconds=value)
        return value

    @property
    def task_execution(self):
        warnings.warn(
            "config.task_execution is deprecated. "
            "Please use config.execution instead.",
            DeprecationWarning
        )
        return self.execution

    @root_validator(pre=True)
    def set_deprecated(cls, values):
        if 'task_execution' in values:
            warnings.warn(
                "Option 'task_execution' is deprecated. "
                "Please use 'execution' instead.",
                DeprecationWarning
            )
            values['execution'] = values.pop('task_execution')
        return values

class Hooks(BaseModel):
    task_init: List[Callable] = []
    task_execute: List[Callable] = []

    scheduler_startup: List[Callable] = []
    scheduler_cycle: List[Callable] = []
    scheduler_shutdown: List[Callable] = []

class Session(RedBase):
    """Collection of the scheduler objects.

    Parameters
    ----------

    config : dict, optional
        Central configuration for defining behaviour
        of different object and classes in the session.
    tasks : Dict[str, rocketry.core.Task], optional
        Tasks of the session. Can be formed later.
    parameters : parameter-like, optional
        Session level parameters.
    scheme : str or list, optional
        Premade scheme(s) to use to set up logging,
        parameters, setup tasks etc.
    as_default : bool, default=True
        Whether to set the session as default for next
        tasks etc. that don't have session
        specified.
    kwds_scheduler : dict, optional
        Keyword arguments passed to
        :py:class:`rocketry.core.Scheduler`.
    delete_existing_loggers : bool, default=False
        If True, deletes the loggers that already existed
        for the task logger basename.

    Attributes
    ----------
    config : dict
        Central configuration for defining behaviour
        of different object and classes in the session.
    scheduler : Scheduler
        Scheduler of the session.
    delete_existing_loggers : bool
        If True, all loggers that match the
        session.config.basename are deleted (by
        default, deletes loggers starting with
        'rocketry.task').

    """
    config: Config
    class Config:
        arbitrary_types_allowed = True

    tasks: Set['Task']
    hooks: Hooks
    parameters: 'Parameters'
    _scheduler: 'Scheduler'

    _time_parsers: ClassVar[Dict] = {}
    _cls_cond_parsers: ClassVar[Dict] = {} # Default condition parsers

    def _get_parameters(self, value):
        from rocketry.core import Parameters
        if value is None:
            return Parameters()
        if not isinstance(value, Parameters):
            value = Parameters(value)
        return value

    def _get_config(self, value, kwargs):
        if value is None:
            return Config(**kwargs)
        if isinstance(value, dict):
            return Config(**value, **kwargs)
        if isinstance(value, Config):
            return value
        raise TypeError("Invalid config type")

    @staticmethod
    def _get_task_name(task):
        from rocketry.core import Task
        if isinstance(task, str):
            task_name = task
        elif hasattr(task, "__rocketry__"):
            # Function that FuncTask set the rocketry info
            task_name = task.__rocketry__['name']
        elif isinstance(task, Task):
            task_name = task.name
        else:
            raise TypeError(f"Cannot determine task name from: {type(task)}")
        return task_name

    def __init__(self, config=None, parameters=None, delete_existing_loggers=False, **kwargs):
        from rocketry.core import Scheduler
        self.config = self._get_config(config, kwargs)
        self.parameters = self._get_parameters(parameters)
        self.scheduler = Scheduler(self)
        self.tasks = set()
        self.hooks = Hooks()
        self.returns = self._get_parameters(None)
        self._cond_parsers = self._cls_cond_parsers.copy()
        self._cond_cache: Dict = {} # Cached by CondParser to speed up expensive conditions
        self._cond_states = {} # Used by FuncConds to relay condiiton states to conditions
        if delete_existing_loggers:
            self.delete_task_loggers()

    def __getitem__(self, task:Union['Task', str]):
        "Get a task from the session"
        task_name = self._get_task_name(task)
        for task in self.tasks:
            if task.name == task_name:
                return task
        raise KeyError(f"Task '{task_name}' not found")

    def __contains__(self, task: Union['Task', str]):
        "Check if task is in session"
        try:
            self[task]
        except KeyError:
            return False
        else:
            return True

    def start(self):
        """Start the scheduling session.

        Will block and wait till the scheduler finishes
        if there is a shut condition."""
        self._set_configs()
        self._wrap_log_record_creation()
        self.scheduler()

    async def serve(self):
        """Start the scheduling session using async.

        Will block and wait till the scheduler finishes
        if there is a shut condition."""
        self._set_configs()
        await self.scheduler.serve()

    def run(self, *task_names:Tuple[str], execution=None, obey_cond=False):
        """Run specific task(s) manually.

        This method starts up the scheduler but only the given
        task is run. Useful to manually run a task while using
        the setup/teardown and parameters of the session and
        scheduler.

        Parameters
        ----------
        *task_names : tuple of str
            Names of the tasks to run.
        execution : str
            Execution method for all of the tasks.
            By default, whatever set to each task
        obey_cond : bool
            Whether to obey the ``start_cond`` or
            force a run regardless. By default, False

        .. warning::

            This is not meant to be called by tasks or the system
            itself. Just to run specific tasks when the system itself
            is not running.
        """
        self._set_configs()
        # To prevent circular import
        from rocketry.conditions.scheduler import SchedulerCycles

        orig_vals = {}
        for task in self.tasks:
            name = task.name
            orig_vals[name] = {
                attr: val for attr, val in task.__dict__.items()
                if attr not in ("status", "last_run", "last_success", "last_fail", "last_terminate")
            }
            if name in task_names:
                if not obey_cond:
                    task.run()
                if execution is not None:
                    task.execution = execution
            else:
                task.disabled = True

        orig_shut_cond = self.config.shut_cond
        try:
            self.config.shut_cond = SchedulerCycles() >= 1
            self.start()
        finally:
            self.config.shut_cond = orig_shut_cond
            # Set back the disabled, execution etc.
            for task in self.tasks:
                task.__dict__.update(orig_vals[task.name])

    def restart(self):
        """Restart the scheduler

        The restart is not instantenous and
        will occur after the scheduler finishes
        checking one cycle of tasks."""
        self.scheduler._flag_restart.set()

    def shutdown(self):
        """Shut down the scheduler

        The shut down is not instantenous and
        will occur after the scheduler finishes
        checking one cycle of tasks."""
        warnings.warn((
            "Session.shutdown is deprecated. "
            "Please use Session.shut_down instead"
        ), DeprecationWarning)
        self.scheduler._flag_shutdown.set()

    def shut_down(self, force=None):
        """Shut down the scheduler"""
        force = force if force is not None else self.scheduler._flag_shutdown.is_set()
        self.scheduler._flag_shutdown.set()
        if force:
            self.scheduler._flag_force_exit.set()

    def _set_configs(self):
        self._check_readable_logger()
        self._wrap_log_record_creation()

    def _check_readable_logger(self):
        from rocketry.core.log import TaskAdapter
        task_logger_basename = self.config.task_logger_basename
        task_logger = logging.getLogger(task_logger_basename)
        logger = TaskAdapter(task_logger, None, ignore_warnings=True)
        if logger.is_readable_unset:
            # Setting memory logger
            warnings.warn(
                f"Logger {task_logger_basename} cannot be read. "
                "Logging is set to memory. "
                "To supress this warning, "
                "please set a handler that can be read (redbird.logging.RepoHandler)", UserWarning)

            # Setting memory logger
            task_logger.addHandler(create_default_handler())
        is_info_logged = logger.getEffectiveLevel() <= logging.INFO
        if not is_info_logged:
            level_name = logging.getLevelName(task_logger.getEffectiveLevel())
            warnings.warn(
                f"Logger {task_logger_basename} has too low level ({level_name}). "
                "Level is set to INFO to make sure the task logs get logged. ", UserWarning)
            task_logger.setLevel(logging.INFO)

    def _wrap_log_record_creation(self, logger=None):
        # Make 
        from rocketry.core.log import TaskAdapter
        if logger is None:
            logger = logging.getLogger(self.config.task_logger_basename)
        attr = '__rocketry_wrapped__'
        is_wrapped = getattr(logger, attr, False)
        wrap_logger = self.config.time_func is not None and not is_wrapped
        if wrap_logger:
            logger.makeRecord = TaskAdapter._modify_record(logger.makeRecord, session=self)
            setattr(logger, attr, True)

    def get_tasks(self) -> list:
        """Get session tasks as list.

        Returns
        -------
        list[rocketry.core.Task]
            List of tasks in the session.
        """
        return self.tasks

    def get_task(self, task):
        warnings.warn((
            "Method get_task will be removed in the future version."
            "Please use instead: session['task name']"
        ), DeprecationWarning)
        return self[task]

    def get_cond_parsers(self):
        "Used by the actual string condition parser"
        return self._cond_parsers

    def create_task(self, *, command=None, path=None, **kwargs):
        "Create a task and put it to the session"

        # To avoid circular imports
        from rocketry.tasks import CommandTask, FuncTask

        kwargs['session'] = self

        if command is not None:
            return CommandTask(command=command, **kwargs)
        if path is not None:
            # Non-wrapped FuncTask
            return FuncTask(path=path, **kwargs)
        return FuncTask(name_include_module=False, _name_template='{func_name}', **kwargs)

    def add_task(self, task: 'Task'):
        "Add the task to the session"
        if_exists = self.config.task_pre_exist
        exists = task in self
        if exists:
            if if_exists == 'ignore':
                return
            if if_exists == 'replace':
                self.tasks.remove(task)
                self.tasks.add(task)
            elif if_exists == 'raise':
                raise KeyError(f"Task '{task.name}' already exists")
        else:
            self.tasks.add(task)

        # Adding the session to the task
        task.session = self

    def remove_task(self, task: Union['Task', str]):
        from rocketry.core.task import Task
        if not isinstance(task, Task):
            task = self[task]
        self.tasks.remove(task)

    def task_exists(self, task: 'Task'):
        warnings.warn((
            "Method task_exists will be removed in the future version."
            "Please use instead: 'task name' in session"
        ), DeprecationWarning)

        task_name = self._get_task_name(task)
        for task in self.tasks:
            if task.name == task_name:
                return True
        return False

    def get_repo(self):
        "Get log repo where the task logs are stored"
        from rocketry.core.log import TaskAdapter
        basename = self.config.task_logger_basename
        logger = logging.getLogger(basename)
        return TaskAdapter(logger, task=None)._get_repo()

    def get_task_loggers(self, with_adapters=True) -> Dict[str, Union['TaskAdapter', logging.Logger]]:
        """Get task logger(s) from the session.

        Parameters
        ----------
        with_adapters : bool, optional
            Whether get the loggers wrapped to
            rocketry.core.log.TaskAdapter, by default True

        Returns
        -------
        Dict[str, Union[TaskAdapter, logging.Logger]]
            Dictionary of the loggers (or adapters)
            in which the key is the logger name.
            Placeholders and loggers built for parallelized
            tasks are ignored.
        """
        from rocketry.core.log import TaskAdapter

        basename = self.config.task_logger_basename
        return {
            # The adapter should not be used to log (but to read) thus task_name = None
            name: TaskAdapter(logger, None) if with_adapters else logger
            for name, logger in logging.root.manager.loggerDict.items()
            if name.startswith(basename)
            and not isinstance(logger, logging.PlaceHolder)
            and not name.endswith("_process") # No private
        }

# Log data
    def get_task_log(self, *args, **kwargs) -> Iterable[Dict]:
        """Get task log records from all of the
        readable handlers in the session.

        Parameters
        ----------
        **kwargs : dict
            Query parameters passed to
            rocketry.core.log.TaskAdapter.get_records

        Returns
        -------
        Iterable[Dict]
            Generator of the task log records.
        """
        loggers = self.get_task_loggers(with_adapters=True)
        data = iter(())
        for logger in loggers.values():
            data = chain(data, logger.get_records(*args, **kwargs))
        return data

    def delete_task_loggers(self):
        """Delete the previous loggers from task logger"""
        loggers = logging.Logger.manager.loggerDict
        for name in list(loggers):
            if name.startswith(self.config.task_logger_basename):
                del loggers[name]

    def clear(self):
        """Clear tasks, parameters etc. of the session"""
        #! TODO: Remove?
        from rocketry.core import Parameters

        self.tasks = set()
        self.parameters = Parameters()

    def __getstate__(self):
        # NOTE: When a process task is executed, it will pickle
        # the task.session. Therefore removing unpicklable here.
        state = self.__dict__.copy()
        state["tasks"] = set()
        state["_cond_cache"] = None
        state["_cond_parsers"] = None
        state["session"] = None
        #state["parameters"] = None
        state['scheduler'] = None
        return state

    def _copy_pickle(self):
        # Copy and remove typically unpicklable attrs.
        # Used when creating a child process
        unpicklable_conf = {'shut_cond'}
        unpicklable = {'tasks', '_cond_cache', 'session', '_cond_parsers', 'parameters'}
        new_self = copy(self)
        for attr in unpicklable:
            setattr(new_self, attr, None)
        new_self.config = self.config.copy(exclude=unpicklable_conf)
        return new_self

    @property
    def env(self):
        "Shorthand for parameter 'env'"
        return self.parameters.get("env")

    @env.setter
    def env(self, value):
        "Shorthand for parameter 'env'"
        self.parameters["env"] = value

    def set_as_default(self):
        """Set this session as the default session for
        next tasks, conditions and schedulers that
        are created.
        """

        RedBase.session = self

        import rocketry
        rocketry.session = self

    def hook_startup(self):
        def wrapper(func):
            self.hooks.scheduler_startup.append(func)
            return func
        return wrapper

    def hook_shutdown(self):
        def wrapper(func):
            self.hooks.scheduler_shutdown.append(func)
            return func
        return wrapper

    def hook_scheduler_cycle(self):
        def wrapper(func):
            self.hooks.scheduler_cycle.append(func)
            return func
        return wrapper

    def hook_task_init(self):
        def wrapper(func):
            self.hooks.task_init.append(func)
            return func
        return wrapper

    def hook_task_execute(self):
        def wrapper(func):
            self.hooks.task_execute.append(func)
            return func
        return wrapper

    def get_current_time(self) -> datetime.datetime:
        """Get measurement of time as datetime
        
        This method is used internally thoroughout
        the package.
        """
        return self._format_timestamp(time.time())

    def get_time(self) -> float:
        if self.config.time_func is not None:
            # Custom time measurement
            return self.config.time_func()
        return time.time()

    def _get_datetime_now(self):
        return self._format_timestamp(self.get_time())

    def _format_timestamp(self, dt:float):
        return datetime.datetime.fromtimestamp(dt, tz=self.config.timezone)
