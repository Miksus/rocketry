
from pickle import PicklingError
import sys
import time
import datetime
import logging
import platform
import traceback
from itertools import count
from types import TracebackType
import warnings
from copy import copy
from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Callable, List, Dict, Type, Union, Tuple, Optional, get_type_hints
import multiprocessing
import threading
from queue import Empty

import pandas as pd
from redengine.arguments.builtin import Return

from redengine._base import RedBase
from redengine.core.condition import BaseCondition, AlwaysTrue, AlwaysFalse, All, set_statement_defaults
from redengine.core.time import TimePeriod
from redengine.core.parameters import Parameters
from redengine.core.log import TaskAdapter
from redengine.core.utils import is_pickleable, filter_keyword_args, is_main_subprocess
from redengine.core.exceptions import SchedulerRestart, SchedulerExit, TaskInactionException, TaskTerminationException
from redengine.core.meta import _register
from redengine.core.hook import _Hooker
from redengine.log import QueueHandler

if TYPE_CHECKING:
    from redengine import Session
    from redengine.core.parameters import BaseArgument

_IS_WINDOWS = platform.system()

class _TaskMeta(type):
    def __new__(mcs, name, bases, class_dict):

        cls = type.__new__(mcs, name, bases, class_dict)

        # Store the name and class for configurations
        if cls.session is not None:
            _register(cls, cls.session.cls_tasks)
        return cls


class Task(RedBase, metaclass=_TaskMeta):
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
    description : str, optional
        Description of the task. This is purely
        for task documentation purpose.
    start_cond : BaseCondition, optional
        Condition that when True the task
        is to be started, by default AlwaysFalse()
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
    timeout : str, int, pd.Timedelta, optional
        If the task has not run in given timeout
        the task will be terminated. Only applicable
        for tasks with execution='process' or 
        with execution='thread'. Passed to 
        ``pandas.Timedelta``.
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
    session : redengine.session.Session, optional
        Session the task is binded to, 
        by default default session 


    Attributes
    ----------
    return_arg: Type of :class:`.BaseArgument`
        Argument class to use to store the return value,
        by default :class:`.Return`
    session : redengine.session.Session
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

    # Class
    permanent_task: bool = False # Whether the task is not meant to finish (Ie. RestAPI)
    _actions: Tuple = ("run", "fail", "success", "inaction", "terminate", None, "crash_release")
    fmt_log_message = r"Task '{task}' status: '{action}'"

    daemon: Optional[bool]

    session: 'Session'
    return_arg: Type['BaseArgument'] = Return

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

    start_cond: BaseCondition
    end_cond: BaseCondition

    on_startup: bool
    on_shutdown: bool

    last_run: Optional[datetime.datetime]
    last_success: Optional[datetime.datetime]
    last_fail: Optional[datetime.datetime]
    last_terminate: Optional[datetime.datetime]
    last_inaction: Optional[datetime.datetime]

    def __init__(self, 
                 parameters=None, 
                 session=None,
                 start_cond: BaseCondition=None, 
                 end_cond: BaseCondition=None, 
                 timeout=None, 
                 priority: int=None,
                 name: str=None, 
                 description: str=None, 
                 logger: logging.Logger=None, 
                 daemon: bool=None,
                 execution: str=None, 
                 disabled: bool=False, 
                 force_run: bool=False,
                 on_startup: bool=False, 
                 on_shutdown: bool=False,
                 on_exists: str=None):

        hooker = _Hooker(self.session.hooks['task_init'])
        hooker.prerun(self)

        self.session = self.session if session is None else session

        self.set_name(name, on_exists=on_exists, register=False)
        self.description = description
        self.logger = logger
        
        self.status = None

        self.start_cond = AlwaysFalse() if start_cond is None else copy(start_cond) # If no start_condition, won't run except manually
        self.end_cond = AlwaysFalse() if end_cond is None else copy(end_cond)

        self.timeout = (
            pd.Timedelta.max # "never" is 292 years
            if timeout == "never"
            else pd.Timedelta(timeout)
            if timeout is not None 
            else timeout
        )
        self.priority = priority or self.session.config['task_priority']

        self.execution = execution or self.session.config['task_execution']
        self.daemon = daemon

        self.on_startup = on_startup
        self.on_shutdown = on_shutdown

        self.disabled = disabled
        self.force_run = force_run
        self.force_termination = False

        self.parameters = parameters

        # Thread specific (readonly properties)
        self._thread_terminate = threading.Event()
        self._lock = threading.Lock() # So that multiple threaded tasks/scheduler won't simultaneusly use the task

        self._set_default_task()

        # Caches
        self._last_run = self._get_last_action_from_log("run")
        self._last_success = self._get_last_action_from_log("success")
        self._last_fail = self._get_last_action_from_log("fail")
        self._last_terminate = self._get_last_action_from_log("terminate")
        self._last_inaction = self._get_last_action_from_log("inaction")

        self.register()
        
        # Hooks
        hooker.postrun()

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

        # The parameters are handled in the following way:
        #   - First extra parameters are fetched. This includes:
        #       - session.parameters
        #       - _task_, _session_, _thread_terminate_
        #   - Then these extras are prefiltered (called params)
        #   - Then the task parameters are fetched (direct_params)
        #   - If process/thread, these parameters are pre_materialized
        #   - Then the params are post filtered
        #   - Then params and direct_params are fed to the execute method

        try:
            params = self.get_extra_params(params)
            # Run the actual task
            if self.execution == "main":
                direct_params = self.parameters
                self._run_as_main(params=params, direct_params=direct_params, execution="main", **kwargs)
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
        except (SchedulerRestart, SchedulerExit):
            raise
        except Exception as exc:
            # Something went wrong in the initiation
            # and it did not reach to log_running
            self.log_running()
            self.log_failure()
            raise

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

    def run_as_main(self, params:Parameters):
        return self._run_as_main(params, self.parameters)

    def _run_as_main(self, params:Parameters, direct_params:Parameters, execution=None, **kwargs):
        """Run the task on the current thread and process"""
        #self.logger.info(f'Running {self.name}', extra={"action": "run"})

        #old_cwd = os.getcwd()
        #if cwd is not None:
        #    os.chdir(cwd)

        # (If SystemExit is raised, it won't be catched in except Exception)
        hooker = _Hooker(self.session.hooks['task_execute'])
        hooker.prerun(self)

        status = None
        output = None
        exc_info = (None, None, None)
        params = self.postfilter_params(params)
        params = Parameters(params) | Parameters(direct_params)
        params = params.materialize(task=self)

        if execution == 'main':
            self.log_running()
        try:
            output = self.execute(**params)

            # NOTE: we process success here in case the process_success
            # fails (therefore task fails)
            self.process_success(output)
        except (SchedulerRestart, SchedulerExit):
            # SchedulerRestart is considered as successful task
            self.log_success()
            status = "succeeded"
            self.process_success(None)
            exc_info = sys.exc_info()
            # Note that these are never silenced
            raise

        except TaskInactionException:
            # Task did not fail, it did not succeed:
            #   The task started but quickly determined was not needed to be run
            #   and therefore the purpose of the task was not executed.
            self.log_inaction()
            status = "inaction"
            exc_info = sys.exc_info()
            
        except TaskTerminationException:
            # Task was terminated and the task's function
            # did listen to that.
            self.log_termination()
            status = "termination"
            exc_info = sys.exc_info()

        except Exception as exception:
            # All the other exceptions (failures)
            try:
                self.process_failure(*sys.exc_info())
            except:
                # Failure of failure processing
                self.log_failure()
            else:
                self.log_failure()
            status = "failed"
            #self.logger.error(f'Task {self.name} failed', exc_info=True, extra={"action": "fail"})

            self.exception = exception
            exc_info = sys.exc_info()
            if execution is None:
                raise

        else:
            # Store the output
            if execution != 'process':
                self._handle_return(output)
            self.log_success(output)
            #self.logger.info(f'Task {self.name} succeeded', extra={"action": "success"})
            status = "succeeded"
            
            return output

        finally:
            self.process_finish(status=status)
            self.force_run = None
            #if cwd is not None:
            #    os.chdir(old_cwd)
            hooker.postrun(*exc_info)

    def run_as_thread(self, params:Parameters, **kwargs):
        """Create a new thread and run the task on that."""

        params = params.pre_materialize(task=self)
        direct_params = self.parameters.pre_materialize()

        self.thread_terminate.clear()

        event_is_running = threading.Event()
        self._thread = threading.Thread(target=self._run_as_thread, args=(params, direct_params, event_is_running))
        self._last_run = datetime.datetime.fromtimestamp(time.time()) # Needed for termination
        self._thread.start()
        event_is_running.wait() # Wait until the task is confirmed to run 
 
    def _run_as_thread(self, params:Parameters, direct_params:Parameters, event=None):
        """Running the task in a new thread. This method should only
        be run by the new thread."""

        self.log_running()
        event.set()
        try:
            output = self._run_as_main(params=params, direct_params=direct_params, execution="thread")
        except:
            # Task crashed before actually running the execute.
            self.log_failure()
            # We cannot rely the exception to main thread here
            # thus we supress to prevent unnecessary warnings.

    def run_as_process(self, params:Parameters, daemon=None):
        """Create a new process and run the task on that."""

        params = params.pre_materialize(task=self)
        direct_params = self.parameters.pre_materialize()

        # Daemon resolution: task.daemon >> scheduler.tasks_as_daemon
        log_queue = self.session.scheduler._log_queue #multiprocessing.Queue(-1)

        daemon = self.daemon if self.daemon is not None else self.session.scheduler.tasks_as_daemon
        self._process = multiprocessing.Process(
            target=self._run_as_process, 
            args=(params, direct_params, log_queue), 
            daemon=daemon
        ) 
        self._last_run = datetime.datetime.fromtimestamp(time.time()) # Needed for termination
        self._mark_running = True # needed in pickling
        
        self._process.start()
        del self._mark_running
        
        self._lock_to_run_log(log_queue)
        return log_queue

    def _run_as_process(self, params:Parameters, direct_params:Parameters, queue):
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
        except:
            logger.critical(f"Task '{self.name}' crashed in setting up logger.", exc_info=True, extra={"action": "fail", "task_name": self.name})
            raise
        self.log_running()
        try:
            # NOTE: The parameters are "materialized" 
            # here in the actual process that runs the task
            output = self._run_as_main(params=params, direct_params=direct_params, execution="process")
        except Exception as exc:
            # Task crashed before running execute (silence=True)
            self.log_failure()

            # There is nothing to raise it
            # to :(
            pass

    def get_extra_params(self, params:Parameters) -> Parameters:
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

        params = Parameters(self.prefilter_params(session_params | passed_params | extra_params))

        return params

    def prefilter_params(self, params:Parameters):
        """Pre filter the parameters.
        
        This method filters the task parameters before 
        a thread or a process is created. This method 
        always called in the main process and in the 
        main thread. Therefore, one can filter here the 
        parameters that are problematic to pass to a 
        thread or process. 

        Parameters
        ----------
        params : redengine.core.Parameters

        Returns
        -------
        Parameters : dict, redengine.core.Parameters
            Filtered parameters.
        """
        return filter_keyword_args(self.execute, params)

    def postfilter_params(self, params:Parameters):
        """Post filter the parameters.
        
        This method filters the task parameters after 
        a thread or a process is created. This method 
        called in the child process, if ``execution='process'``, 
        or in the child thread ``execution='thread'``.
        For ``execution='main'``, overriding this method
        does not have much impact over overriding 
        ``prefilter_params``.

        Parameters
        ----------
        params : redengine.core.Parameters

        Returns
        -------
        Parameters : dict, redengine.core.Parameters
            Filtered parameters.
        """
        return params

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Run the actual task. Override this.
        
        Parameters are materialized to keyword arguments.
        """
        raise NotImplementedError(f"Method 'execute' not implemented to {type(self)}.")

    def process_failure(self, exc_type:Type[Exception], exc_val:Exception, exc_tb:TracebackType):
        """This method is executed after a failure of the task. 
        Override if needed.
        
        Parameters
        ----------
        exc_type : subclass of Exception
            Type of the occurred exception that caused the failure.
        exc_val : Exception
            Exception that caused the failure. 
        exc_type : Traceback object
            Traceback of the failure exception.
        """
        pass
    
    def process_success(self, output:Any):
        """This method is executed after a success of the task. 
        Override if needed.
        
        Parameters
        ----------
        output : Any
            Return value of the task.
        """
        pass

    def process_finish(self, status:str):
        """This method is executed after finishing the task. 
        Override if needed.
        
        Parameters
        ----------
        status : str {'succeeded', 'failed', 'termination', 'inaction'}
            How the task finished.
        """
        pass

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

    @property
    def execution(self) -> str:
        """str: Execution of the task"""
        return self._execution
    
    @execution.setter
    def execution(self, execution:str):
        allowed = ("main", "thread", "process")
        if execution not in allowed:
            raise ValueError(f"Execution {execution:!r} not valid. Options: {allowed}")
        self._execution = execution

    def set_name(self, name, on_exists=None, use_instance_naming=None, register=True):
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
                pass

            elif on_exists == "raise":
                raise KeyError(f"Task {name} already exists. (All tasks: {self.session.tasks})")

            elif on_exists == "ignore":
                self._mark_register = False

            elif on_exists == "rename":
                for i in count():
                    new_name = name + str(i)
                    if new_name not in self.session.tasks:
                        name = new_name
                        break

        self._name = str(name)
        if register:
            self.session.tasks[name] = self
            if old_name is not None:
                del self.session.tasks[old_name]

    def register(self):
        if hasattr(self, "_mark_register") and not self._mark_register:
            del self._mark_register
            return # on_exists = 'ignore'
        name = self.name
        self.session.tasks[name] = self

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
        self.status = "fail"

    def log_success(self, return_value=None):
        """Make a log that the task succeeded."""
        self._set_status("success", return_value=return_value)
        #self.status = "success"

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
        # Set last_run/last_success/last_fail etc.
        cache_attr = f"_last_{record.action}"
        record_time = datetime.datetime.fromtimestamp(record.created)
        setattr(self, cache_attr, record_time)

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
                if is_main_subprocess():
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
            value, message = value
        else:
            message = None
        self._set_status(value, message)

    def _set_status(self, action, message=None, return_value=None):
        if message is None:
            message = self.fmt_log_message.format(action=action, task=self.name)

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
            
            is_running_as_child = self.logger.name.endswith("._process")
            if is_running_as_child and action == "success":
                # If child process, the return value is passed via QueueHandler to the main process
                # and it's handled then in Scheduler.
                # Else the return value is handled in Task itself (__call__ & _run_as_thread)
                extra["__return__"] = return_value

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
        """datetime.datetime: The lastest timestamp when the task terminated."""
        return self._get_last_action("terminate")

    @property
    def last_inaction(self):
        """datetime.datetime: The lastest timestamp when the task inacted."""
        return self._get_last_action("inaction")

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
            if is_main_subprocess():
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

        
        if not is_pickleable(state):
            if self._mark_running:
                # When this block might get executed?
                #   - If FuncTask func is non-picklable
                #       - There is another func with same name in the file
                #       - The function is lambda or decorated func
                unpicklable = {key: val for key, val in state.items() if not is_pickleable(val)}
                self.log_running()
                self.logger.critical(f"Task '{self.name}' crashed in pickling. Cannot pickle: {unpicklable}", extra={"action": "fail", "task_name": self.name})
                raise PicklingError(f"Task {self.name} could not be pickled. Cannot pickle: {unpicklable}")
            else:
                # Is pickled by something else than task execution
                return state

        # what we return here will be stored in the pickle
        return state

    @property
    def thread_terminate(self) -> threading.Event:
        """threading.Event: Event to signal terminating the threaded task.
        This property should be used by the execute of the task."""
        # Readonly "attribute"
        return self._thread_terminate

    def _handle_return(self, value):
        "Handle the return value (ie. store to parameters)"
        self.return_arg.to_session(self.name, value)

    def delete(self):
        """Delete the task from the session. 
        Overried if needed additional cleaning."""
        del self.session.tasks[self.name]

    @property
    def lock(self):
        #! TODO: Is this needed?
        return self._lock

# Hooks
    @classmethod
    def hook_init(cls, func:Callable) -> Callable:
        """Hook task initiation (:class:`Task.__init__ <redengine.core.Task>`)
        with a custom function or generator.
        
        Examples
        --------

        .. testcode::
            :hide:

            cleanup()

        .. doctest::

            >>> from redengine.core import Task
            >>> @Task.hook_init
            ... def do_things(task):
            ...     "This is executed when any task of any type is created"
            ...     print("Init hook was executed.")

            >>> from redengine.tasks import FuncTask
            >>> mytask = FuncTask(lambda: None)
            Init hook was executed.

        .. testcode::
            :hide:
            
            cleanup()

        .. doctest::

            >>> from redengine.core import Task
            >>> @Task.hook_init
            ... def do_things(task):
            ...     "This is executed when any task of any type is created"
            ...     print("Task's __init__ is called.")
            ...     # Note that we are missing some attributes like 'task.name'
            ...     # as those are not yet set.
            ...
            ...     yield
            ...
            ...     # Now we have everything that is set in Task.__init__
            ...     print("Task's __init__ is completed.")

            >>> from redengine.tasks import FuncTask
            >>> mytask = FuncTask(lambda: None)
            Task's __init__ is called.
            Task's __init__ is completed.


        .. testcode::
            :hide:
            
            cleanup()
        """
        cls.session.hooks['task_init'].append(func)
        return func

    @classmethod
    def hook_execute(cls, func:Callable) -> Callable:
        """Hook executing tasks (:class:`Task <redengine.core.Task>`)
        with a custom function or generator.
        
        Examples
        --------
        
        .. code-block:: python

            >>> from redengine.core import Task
            >>> @Task.hook_execute
            ... def do_things(task):
            ...     "This is executed when any task is started"
            ...     print("Run hook was executed.")
            ...     exc_type, exc, tb = yield
            ...     print("After executing a task")
        """
        cls.session.hooks['task_execute'].append(func)
        return func

# Other
    @property
    def period(self) -> TimePeriod:
        """TimePeriod: Time period in which the task runs

        Note that this should not be considered as absolute truth but
        as a best estimate.
        """
        from redengine.core.time import StaticInterval, All as AllTime
        from redengine.conditions import TaskFinished, TaskSucceeded

        cond = self.start_cond
        session = self.session

        if isinstance(cond, (TaskSucceeded, TaskFinished)):
            if session.get_task(cond.kwargs["task"]) is self:
                return cond.period

        elif isinstance(cond, All):
            task_periods = []
            for sub_stmt in cond:
                if isinstance(sub_stmt, (TaskFinished, TaskFinished)) and session.get_task(sub_stmt.kwargs["task"]) is self:
                    task_periods.append(sub_stmt.period)
            if task_periods:
                return AllTime(*task_periods)
        
        # TimePeriod could not be determined
        return StaticInterval()

    def to_dict(self) -> dict:
        """Get dict representation of a task"""
        string_typehints = {'Session': 'Session', 'BaseArgument': 'BaseArgument'}
        cls = type(self)
        type_hints = get_type_hints(cls, string_typehints)
        return {
            attr: getattr(self, attr)
            for attr in type_hints
            if not attr.startswith("_") # ignore private
        }
    
    @classmethod
    def from_dict(cls, conf:dict):
        """Create a task from dict
        
        If called from the base class (``Task.from_dict(...)``)
        the dict should also have specified ``class`` as a key."""
        if cls == Task:
            cls_name = conf.pop('class')
            cls = cls.session.cls_tasks[cls_name]
        return cls(**conf)