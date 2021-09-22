
from redengine.core.condition import BaseCondition, AlwaysTrue, AlwaysFalse, All, set_statement_defaults
from redengine.core.log import TaskAdapter
from redengine.core.utils import is_pickleable
from redengine.core.exceptions import SchedulerRestart, SchedulerExit, TaskInactionException, TaskTerminationException
from redengine.log import QueueHandler

from .utils import get_execution, get_dependencies

from redengine.conditions import DependSuccess
from redengine.core.parameters import Parameters
from redengine.core.meta import _register

import os, time
import platform
import logging
import inspect
import warnings
import datetime
from typing import Callable, List, Dict, Union, Tuple, Type, Optional
import multiprocessing
import threading
from queue import Empty

from functools import wraps
from copy import copy
from itertools import count

import pandas as pd

CLS_TASKS = {}

_IS_WINDOWS = platform.system()


class _TaskMeta(type):
    def __new__(mcs, name, bases, class_dict):

        cls = type.__new__(mcs, name, bases, class_dict)

        # Store the name and class for configurations
        _register(cls, CLS_TASKS)
        return cls


class Task(metaclass=_TaskMeta):
    """Base class for Tasks.

    A task can be a function, command or other procedure that 
    does a specific thing. A task can be parametrized by supplying
    session level parameters or parameters on task basis.
    

    Parameters
    ----------
    name : str, optional
        Name of the task. Ideally, all tasks
        should have unique name. If None, the
        return value of Task.get_default_name() 
        is used instead.
    start_cond : BaseCondition, optional
        Condition that when True the task
        is to be started, by default AlwaysFalse()
    run_cond : BaseCondition, optional
        The task will run as long as this 
        condition is True, by default AlwaysTrue()
    end_cond : BaseCondition, optional
        Condition that when True the task
        will be terminated. Only works for for 
        tasks with execution='process' or 'thread'
        if thread termination is implemented in 
        the task, by default AlwaysFalse()
    execution : str, {'main', 'thread', 'process'}, default='process'
        How the task is executed. Allowed values
        'main' (run on main thread & process), 
        'thread' (run on another thread) and 
        'process' (run on another process).
    parameters : Parameters, optional
        Parameters set specifically to the task, 
        by default None
    disabled : bool
        If True, the task is not allowed to be run
        regardless of the start_cond,
        by default False
    force_run : bool
        If True, the task will be run once 
        regardless of the start_cond,
        by default True
    on_startup : bool
        Run the task on the startup sequence of 
        the Scheduler, by default False
    on_shutdown : bool
        Run the task on the shutdown sequence of 
        the Scheduler, by default False
    priority : int, optional
        Priority of the task. Higher priority
        tasks are first inspected whether they
        can be executed. Can be any numeric value.
        Setup tasks are recommended to have priority
        >= 40 if they require loaded tasks,
        >= 50 if they require loaded extensions.
        By default 0
    timeout : float, optional
        If the task has not run in given timeout
        the task will be terminated. Only applicable
        for tasks with execution='process' or 
        with execution='thread' if the task function
        supports it.
    on_success : Callable, optional
        Function to run after successful execution
        of the task, by default None
    on_failure : Callable, optional
        Function to run after failing execution
        of the task, by default None
    on_finish : Callable, optional
        Function to run after execution
        of the task, by default None
    daemon : Bool, optional
        Whether run the task as daemon process
        or not. Only applicable for execution='process',
        by default use Scheduler default
    on_exists : str
        What to do if the name of the task already 
        exists in the session, options: 'raise',
        'ignore', 'replace', by default use session
        configuration
    logger : str, logger.Logger, optional
        Logger of the task. Typically not needed
        to be set.
    session : Session, optional
        Session the task is binded to, 
        by default default session 

    Attributes
    ----------
    session : Session
        Session the task is binded to.
    logger : TaskAdapter
        Logger of the task. Access the 
        log records using task.logger.get_records()

    Examples
    --------

    Minimum example:

    >>> from redengine.core import Task
    >>> class MyTask(Task):
    ...     def execute(self):
    ...         ... # What the task does.
    ...         return ...

    """
    __register__ = False

    # Class
    use_instance_naming: bool = False
    permanent_task: bool = False # Whether the task is not meant to finish (Ie. RestAPI)
    _actions: Tuple = ("run", "fail", "success", "inaction", "terminate", None, "crash_release")

    daemon: Optional[bool]

    session: 'Session' = None

    # Instance
    name: str
    logger: TaskAdapter
    execution: str
    priority: int
    disabled: bool
    force_run: bool
    force_termination: bool
    status: str
    timeout: pd.Timedelta

    parameters: Parameters
    dependent: List['Task']

    start_cond: BaseCondition
    run_cond: BaseCondition
    end_cond: BaseCondition
    
    on_success: Callable
    on_failure: Callable
    on_finish: Callable

    on_startup: Callable
    on_shutdown: Callable

    last_run: Optional[datetime.datetime]
    last_success: Optional[datetime.datetime]
    last_fail: Optional[datetime.datetime]

    # Class defaults
    default_priority = 0

    def __init__(self, parameters=None, session=None,
                start_cond=None, run_cond=None, end_cond=None, 
                dependent=None, timeout=None, priority=None, 
                on_success=None, on_failure=None, on_finish=None, 
                name=None, logger=None, daemon=None,
                execution="process", disabled=False, force_run=False,
                on_startup=False, on_shutdown=False,
                on_exists=None):

        self.session = self.session if session is None else session

        self.set_name(name, on_exists=on_exists)
        self.logger = logger
        
        self.status = None

        self.start_cond = AlwaysFalse() if start_cond is None else copy(start_cond) # If no start_condition, won't run except manually
        self.run_cond = AlwaysTrue() if run_cond is None else copy(run_cond)
        self.end_cond = AlwaysFalse() if end_cond is None else copy(end_cond)

        self.timeout = (
            pd.Timedelta.max # "never" is 292 years
            if timeout == "never"
            else pd.Timedelta(timeout)
            if timeout is not None 
            else timeout
        )
        self.priority = priority or self.default_priority

        self.execution = execution
        self.daemon = daemon

        self.on_startup = on_startup
        self.on_shutdown = on_shutdown

        self.disabled = disabled
        self.force_run = force_run
        self.force_termination = False

        self.on_failure = on_failure
        self.on_success = on_success
        self.on_finish = on_finish

        self.dependent = dependent
        self.parameters = parameters

        # Thread specific (readonly properties)
        self._thread_terminate = threading.Event()
        self._lock = threading.Lock() # So that multiple threaded tasks/scheduler won't simultaneusly use the task

        # Whether the task is maintenance task
        self.is_maintenance = False

        self._set_default_task()

        # Caches
        self._last_run = self._get_last_action_from_log("run")
        self._last_success = self._get_last_action_from_log("success")
        self._last_fail = self._get_last_action_from_log("fail")
        self._last_terminate = self._get_last_action_from_log("terminate")

    @property
    def start_cond(self):
        """BaseCondition: When True, the task will be started (if not running)."""
        return self._start_cond
    
    @start_cond.setter
    def start_cond(self, cond):
        # Rare exception: We need something from builtins (outside core) to be user friendly
        from redengine.parse.condition import parse_condition
        cond = parse_condition(cond) if isinstance(cond, str) else cond
        self._validate_cond(cond)

        set_statement_defaults(cond, task=self)
        self._start_cond = cond
        
    @property
    def end_cond(self):
        """BaseCondition: When True, the task will be terminated (if running)."""
        return self._end_cond
    
    @end_cond.setter
    def end_cond(self, cond):
        # Rare exception: We need something from builtins (outside core) to be user friendly
        from redengine.parse.condition import parse_condition
        cond = parse_condition(cond) if isinstance(cond, str) else cond
        self._validate_cond(cond)

        set_statement_defaults(cond, task=self)
        self._end_cond = cond

    @property
    def dependent(self):
        #! TODO: Delete
        return get_dependencies(self)

    @dependent.setter
    def dependent(self, tasks:list):
        # tasks: List[str]
        if not tasks:
            # TODO: Remove dependent parts
            return
        dep_cond = All(*(DependSuccess(depend_task=task, task=self.name) for task in tasks))
        self.start_cond &= dep_cond

    @property
    def parameters(self):
        """Parameters: Parameters of the task."""
        return self._parameters

    @parameters.setter
    def parameters(self, val:Union[Dict, Parameters, None]):
        if val is None:
            self._parameters = Parameters()
        else:
            self._parameters = Parameters(val)

    def _validate_cond(self, cond):
        if not isinstance(cond, (BaseCondition, bool)):
            raise TypeError(f"Condition must be bool or inherited from {BaseCondition}. Given: {type(cond)}")

    def _set_default_task(self):
        "Set the task in subconditions that are missing "
        set_statement_defaults(self.start_cond, task=self)
        set_statement_defaults(self.run_cond, task=self)
        set_statement_defaults(self.end_cond, task=self)

    def __call__(self, params:Union[dict, Parameters]=None, **kwargs):
        """Execute the task. Creates a new process
        (if execution='process'), a new thread
        (if execution='thread') or blocks and 
        runs till the task is completed (if 
        execution='main').

        Parameters
        ----------
        params : dict, Parameters, optional
            Extra parameters for the task. Also
            the session parameters, task parameters
            and extra parameters are acquired, by default None
        """

        # Remove old threads/processes
        # (using _process and _threads are most robust way to check if running as process or thread)
        if hasattr(self, "_process"):
            del self._process
        if hasattr(self, "_thread"):
            del self._thread

        params = self.get_extra_params(params)
        # Run the actual task
        if self.execution == "main":
            params = self.postfilter_params(params)
            self.run_as_main(params=params, **kwargs)
            if _IS_WINDOWS:
                #! TODO: This probably is now solved
                # There is an annoying bug (?) in Windows:
                # https://bugs.python.org/issue44831
                # If one checks whether the task has succeeded/failed
                # already the log might show that the task finished 
                # 1 microsecond in the future if memory logging is used. 
                # Therefore we sleep that so condition checks especially 
                # in tests will succeed. 
                time.sleep(1e-6)
        elif self.execution == "process":
            self.run_as_process(params=params, **kwargs)
        elif self.execution == "thread":
            self.run_as_thread(params=params, **kwargs)
        else:
            raise ValueError(f"Invalid execution: {self.execution}")

    def __bool__(self):
        """Check whether the task can be run or not.
        
        If force_run is True, the task can be run regardless.
        If disabled is True, the task is prevented to be run 
        (unless force_true=True). 
        If neither of the previous, the start_cond is inspected
        and if it is True, the task can be run.
        """
        # Also add methods: 
        #    set_pending() : Set forced_state to False
        #    resume() : Reset forced_state to None
        #    set_running() : Set forced_state to True

        if self.force_run:
            return True
        elif self.disabled:
            return False

        cond = bool(self.start_cond)

        return cond

    def run_as_main(self, params:Parameters, _log_running=True, **kwargs):
        """Run the task on the current thread and process"""
        if _log_running:
            self.log_running()
        #self.logger.info(f'Running {self.name}', extra={"action": "run"})

        #old_cwd = os.getcwd()
        #if cwd is not None:
        #    os.chdir(cwd)

        # (If SystemExit is raised, it won't be catched in except Exception)
        status = None
        try:
            params = Parameters(params) | self.parameters
            params = params.materialize()

            output = self.execute(**params)

        except (SchedulerRestart, SchedulerExit):
            # SchedulerRestart is considered as successful task
            self.log_success()
            #self.logger.info(f'Task {self.name} succeeded', extra={"action": "success"})
            status = "succeeded"
            self.process_success(None)
            raise

        except TaskInactionException:
            # Task did not fail, it did not succeed:
            #   The task started but quickly determined was not needed to be run
            #   and therefore the purpose of the task was not executed.
            self.log_inaction()
            status = "inaction"
            
        except TaskTerminationException:
            # Task was terminated and the task's function
            # did listen to that.
            self.log_termination()
            status = "termination"

        except Exception as exception:
            # All the other exceptions (failures)
            self.log_failure()
            status = "failed"
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
            self.force_run = None
            #if cwd is not None:
            #    os.chdir(old_cwd)

    def run_as_thread(self, params:Parameters, **kwargs):
        """Create a new thread and run the task on that."""
        self.thread_terminate.clear()

        event_is_running = threading.Event()
        self._thread = threading.Thread(target=self._run_as_thread, args=(params, event_is_running))
        self._last_run = datetime.datetime.fromtimestamp(time.time()) # Needed for termination
        self._thread.start()
        event_is_running.wait() # Wait until the task is confirmed to run 
 
    def _run_as_thread(self, params:Parameters, event=None):
        """Running the task in a new thread. This method should only
        be run by the new thread."""
        self.log_running()
        event.set()
        # Adding the _thread_terminate as param so the task can
        # get the signal for termination
        #params = Parameters() if params is None else params
        #params = params | {"_thread_terminate_": self._thread_terminate}
        params = self.postfilter_params(params)
        try:
            self.run_as_main(params=params, _log_running=False)
        except:
            # We cannot rely the exception to main thread here
            # thus we supress to prevent unnecessary warnings.
            pass

    def run_as_process(self, params:Parameters, daemon=None):
        """Create a new process and run the task on that."""

        # Daemon resolution: task.daemon >> scheduler.tasks_as_daemon
        log_queue = self.session.scheduler._log_queue #multiprocessing.Queue(-1)
        return_queue = self.session.scheduler._return_queue

        daemon = self.daemon if self.daemon is not None else self.session.scheduler.tasks_as_daemon
        self._process = multiprocessing.Process(target=self._run_as_process, args=(params, log_queue, return_queue), daemon=daemon) 
        self._last_run = datetime.datetime.fromtimestamp(time.time()) # Needed for termination
        self._process.start()
        
        self._lock_to_run_log(log_queue)
        return log_queue

    def _run_as_process(self, params:Parameters, queue, return_queue):
        """Running the task in a new process. This method should only
        be run by the new process."""

        # NOTE: This is in the process and other info in the application
        # cannot be accessed here. Self is a copy of the original
        # and cannot affect main processes' attributes!
        
        # The task's logger has been removed by MultiScheduler.run_task_as_process
        # (see the method for more info) and we need to recreate the logger now
        # in the actual multiprocessing's process. We only add QueueHandler to the
        # logger (with multiprocessing.Queue as queue) so that all the logging
        # records end up in the main process to be logged properly. 

        basename = self.session.config["task_logger_basename"]
        # handler = logging.handlers.QueueHandler(queue)
        handler = QueueHandler(queue)

        # Set the process logger
        logger = logging.getLogger(basename + "._process")
        logger.setLevel(logging.INFO)
        logger.propagate = False
        logger.handlers = []
        logger.addHandler(handler)
        try:
            self.logger = logger
            #task.logger.addHandler(
            #    logging.StreamHandler(sys.stdout)
            #)
            #task.logger.addHandler(
            #    QueueHandler(queue)
            #)
        except:
            logger.critical(f"Task '{self.name}' crashed in setting up logger.", exc_info=True, extra={"action": "fail", "task_name": self.name})
            raise

        params = self.postfilter_params(params)
        try:
            # NOTE: The parameters are "materialized" 
            # here in the actual process that runs the task
            output = self.run_as_main(params=params)
        except Exception as exc:
            # Just catching all exceptions.
            # There is nothing to raise it
            # to :(
            pass
        else:
            if return_queue:
                return_queue.put((self.name, output))

    def get_extra_params(self, params) -> Parameters:
        """Get additional parameters from
        the session and extra for meta tasks
        including the task itself, session 
        and the thread terminate event.
        These parameters may or may not be used
        by the task.


        Included parameters:

        - _session_ : task's session
        - _task_ : the task itself
        - _thread_terminate_ : Task termination event if threading used (threading.Event)

        Returns
        -------
        Parameters
            Additional parameters
        """
        passed_params = Parameters(params)
        session_params = self.session.parameters
        #task_params = Parameters(self.parameters)
        extra_params = Parameters(_session_=self.session, _task_=self, _thread_terminate_=self._thread_terminate)

        return Parameters(self.prefilter_params(session_params | passed_params | extra_params))# | task_params

    def prefilter_params(self, params:Parameters):
        """Filter the parameters before passing them to the processes or threads
        if parallerized"""
        sig = inspect.signature(self.execute)
        kw_args = [
            val.name
            for name, val in sig.parameters.items()
            if val.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD, # Normal argument
                inspect.Parameter.KEYWORD_ONLY # Keyword argument
            )
        ]
        return {
            key: val for key, val in params.items()
            if key in kw_args
        }

    def postfilter_params(self, params:Parameters):
        """Filter the parameters after passing them to the processes or threads
        if parallerized"""
        return params

    def execute(self, *args, **kwargs):
        """Run the actual task. Override this.
        
        Parameters are materialized to the positional and
        keyword arguments."""
        raise NotImplementedError(f"Method 'execute' not implemented to {type(self)}")

    def process_failure(self, exception):
        """This method is executed after a failure of the task. 
        By default, run the on_failure Callable (if not None)"""
        if self.on_failure:
            self.on_failure(exception=exception)
    
    def process_success(self, output):
        """This method is executed after a success of the task. 
        By default, run the on_success Callable (if not None)"""
        if self.on_success:
            self.on_success(output)

    def process_finish(self, status):
        """This method is executed after finishing the task. 
        By default, run the on_finish Callable (if not None)"""
        if self.on_finish:
            self.on_finish(status)

    @property
    def is_running(self):
        """bool: Whether the task is currently running or not."""
        return self.status == "run"

    @property
    def name(self) -> str:
        """str: Name of the task"""
        return self._name
    
    @name.setter
    def name(self, name:str):
        self.set_name(name)

    def set_name(self, name, on_exists=None, use_instance_naming=None):
        """Set the name of the task.

        Parameters
        ----------
        name : str
            Name of this task.
        on_exists : str
            What to do if the name of the task already 
            exists in the session, options: 'raise',
            'ignore', 'replace', by default use session
            configuration
        use_instance_naming : bool, optional
            Use id of the instance if name is not 
            supplied. If False, the result of 
            get_default_name is used instead, 
            by default None

        Raises
        ------
        KeyError
            Task already exists
        """
        on_exists = self.session.config["task_pre_exist"] if on_exists is None else on_exists
        use_instance_naming = self.session.config["use_instance_naming"] if use_instance_naming is None else use_instance_naming

        if name is None:
            name = (
                id(self)
                if use_instance_naming
                else self.get_default_name()
            )

        old_name = None if not hasattr(self, "_name") else self._name
        if name == old_name:
            return
        
        if name in self.session.tasks:
            if on_exists == "replace":
                self.session.tasks[name] = self
            elif on_exists == "raise":
                raise KeyError(f"Task {name} already exists. (All tasks: {self.session.tasks})")
            elif on_exists == "ignore":
                pass
            elif on_exists == "rename":
                for i in count():
                    new_name = name + str(i)
                    if new_name not in self.session.tasks:
                        self.name = new_name
                        return
        else:
            self.session.tasks[name] = self
        
        self._name = str(name)

        if old_name is not None:
            del self.session.tasks[old_name]

    def get_default_name(self):
        """Create a name for the task when name was not passed to initiation of
        the task. Override this method."""
        raise NotImplementedError(f"Method 'get_default_name' not implemented to {type(self)}")

    def is_alive(self) -> bool:
        """Whether the task is alive: check if the task has a live process or thread."""
        return self.is_alive_as_thread() or self.is_alive_as_process()

    def is_alive_as_thread(self) -> bool:
        """Whether the task has a live thread."""
        return hasattr(self, "_thread") and self._thread.is_alive()

    def is_alive_as_process(self) -> bool:
        """Whether the task has a live process."""
        return hasattr(self, "_process") and self._process.is_alive()
        
# Logging
    def _lock_to_run_log(self, log_queue):
        "Handle next run log to make sure the task started running before continuing (otherwise may cause accidential multiple launches)"
        action = None
        timeout = 10 # Seconds allowed the setup to take before declaring setup to crash
        #record = log_queue.get(block=True, timeout=None)
        while action != "run":
            try:
                record = log_queue.get(block=True, timeout=timeout)
            except Empty:
                if not self.is_alive():
                    # There will be no "run" log record thus ending the task gracefully
                    self.logger.critical(f"Task '{self.name}' crashed in setup", extra={"action": "fail"})
                    return
            else:
                
                self.logger.debug(f"Inserting record for '{record.task_name}' ({record.action})")
                task = self.session.get_task(record.task_name)
                task.log_record(record)

                action = record.action

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, logger:Union[str, logging.Logger, None]):
        """Set the logger of the task

        Parameters
        ----------
        logger : str, logging.Logger, None
            Logger for the task. If None, 
            the logger from session config
            is set.
        """
        basename = self.session.config["task_logger_basename"]
        if logger is None:
            # Get class logger (default logger)
            logger = logging.getLogger(basename)
        if isinstance(logger, str):
            logger = logging.getLogger(logger)

        if not logger.name.startswith(basename):
            raise ValueError(f"Logger name must start with '{basename}' as session finds loggers with names")

        if not isinstance(logger, TaskAdapter):
            logger = TaskAdapter(logger, task=self)
        self._logger = logger

    def log_running(self):
        """Make a log that the task is currently running."""
        self.status = "run"

    def log_failure(self):
        """Log that the task failed."""
        self.status = "fail", f"Task '{self.name}' failed"

    def log_success(self):
        """Make a log that the task succeeded."""
        self.status = "success"

    def log_termination(self, reason=None):
        """Make a log that the task was terminated."""
        reason = reason or "unknown reason"
        self.status = "terminate", reason

        # Reset event and force_termination (for threads)
        self.thread_terminate.clear()
        self.force_termination = False

    def log_inaction(self):
        """Make a log that the task did nothing."""
        self.status = "inaction"

    def log_record(self, record:logging.LogRecord):
        """Log the record with the logger of the task.
        Also sets the status according to the record.
        """
        self.logger.handle(record)
        self._status = record.action

    @property
    def status(self):
        """str: Latest status of the task. 
        Values: None, 'run', 'fail', 'success', 'terminate' and 'inaction'"""
        if self.session.config["force_status_from_logs"]:
            try:
                record = self.logger.get_latest()
            except AttributeError:
                warnings.warn(f"Task '{self.name}' logger is not readable. Status unknown.")
                record = None
            if not record:
                # No previous status
                return None
            return record["action"]
        else:
            # This is way faster
            return self._status

    @status.setter
    def status(self, value:Union[str, Tuple[str, str]]):
        "Set status (and log the status) of the scheduler"
        if isinstance(value, tuple):
            action = value[0]
            message = value[1]
        else:
            action = value
            message = f"Task '{self.name}' status: '{value}'"
        if action not in self._actions:
            raise KeyError(f"Invalid action: {action}")
        
        if action is not None:
            now = datetime.datetime.fromtimestamp(time.time())
            if action == "run":
                extra = {"action": "run", "start": now}
                # self._last_run = now
            else:
                start_time = self._last_run
                runtime = now - start_time if start_time is not None else None
                extra = {"action": action, "start": start_time, "end": now, "runtime": runtime}
            
            log_method = self.logger.exception if action == "fail" else self.logger.info
            log_method(
                message, 
                extra=extra
            )
            cache_attr = f"_last_{action}"
            setattr(self, cache_attr, now)
        self._status = action

    @property
    def last_success(self):
        """datetime.datetime: The lastest timestamp when the task succeeded."""
        return self._get_last_action("success")

    @property
    def last_fail(self):
        """datetime.datetime: The lastest timestamp when the task failed."""
        return self._get_last_action("fail")

    @property
    def last_run(self):
        """datetime.datetime: The lastest timestamp when the task ran."""
        return self._get_last_action("run")

    @property
    def last_terminate(self):
        """datetime.datetime: The lastest timestamp when the task ran."""
        return self._get_last_action("terminate")

    def _get_last_action(self, action):
        cache_attr = f"_last_{action}"

        allow_cache = not self.session.config["force_status_from_logs"]
        if allow_cache: #  and getattr(self, cache_attr) is not None
            return getattr(self, cache_attr)
        else:
            return self._get_last_action_from_log(action)

    def _get_last_action_from_log(self, action):
        """Get last action timestamp from log"""
        try:
            record = self.logger.get_latest(action=action)
        except AttributeError:
            warnings.warn(f"Task '{self.name}' logger is not readable. Latest {action} unknown.")
            return None
        else:
            if not record:
                return None
            timestamp = record["timestamp"]
            return timestamp

    def __getstate__(self):

        # capture what is normally pickled
        state = self.__dict__.copy()

        # remove unpicklable
        # TODO: Include conditions by enforcing tasks are passed to the conditions as names
        state['_logger'] = None
        state['_start_cond'] = None
        state['_end_cond'] = None
        state["_process"] = None # If If execution == "process"
        state["_thread"] = None # If execution == "thread"

        state["_thread_terminate"] = None # Event only for threads

        state["_lock"] = None # Process task cannot lock anything anyways

        # what we return here will be stored in the pickle
        return state

    @property
    def thread_terminate(self) -> threading.Event:
        """threading.Event: Event to signal terminating the threaded task.
        This property should be used by the execute of the task."""
        # Readonly "attribute"
        return self._thread_terminate

    def delete(self):
        """Delete the task from the session. 
        Overried if needed additional cleaning."""
        del self.session.tasks[self.name]

    @property
    def lock(self):
        #! TODO: Is this needed?
        return self._lock

# Other
    @property
    def period(self):
        "Determine Time object for the interval (maximum possible if time independent as 'or')"
        #! TODO: Is this needed?
        return get_execution(self)