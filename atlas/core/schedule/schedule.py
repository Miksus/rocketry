


from multiprocessing import Process, cpu_count
import multiprocessing

import traceback
import warnings
import time
import sys, os
import logging
from logging.handlers import QueueHandler
import datetime
from pathlib import Path
from copy import deepcopy, copy
from queue import Empty

import pandas as pd

from atlas.core.task.base import Task, get_task
from atlas.core.log import FilterAll, read_logger

from .exceptions import SchedulerRestart

from atlas.core.utils import is_pickleable
from atlas.core.conditions import set_statement_defaults
from atlas.core.parameters import Parameters, GLOBAL_PARAMETERS

# TODO: Controlled crashing
#   Wrap __call__ with a decor that has try except

_SCHEDULERS = {} # Probably will be only one but why not support multiple?

def get_all_schedulers():
    return _SCHEDULERS

def get_scheduler(sched):
    if isinstance(sched, Scheduler):
        return sched
    return _SCHEDULERS[sched]

def clear_schedulers():
    global _SCHEDULERS
    _SCHEDULERS = {}
    

class Scheduler:
    """
    One treaded Scheduler 

    Flow of action:
    ---------------
        __call__() : Start and run the scheduler
            setup() : Set up the scheduler (set up scheduler logger etc.)
            Check and possibly run runnable tasks until shut_condition is not met
                hibernate() : Put scheduler to sleep (to throttle down the scheduler)
                run_cycle() : Iterate tasks once through and run tasks that can be run 
                    Check if task's start_cond is met. If it is:
                        run_task() : Executes the actual task
                            Task.__call__() : Handles logging and how the task is run
                maintain() : Run maintanance tasks that may operate on the scheduler

    """

    _logger_basename = __name__
    logger = logging.getLogger(_logger_basename)
    parameters = GLOBAL_PARAMETERS # interfacing the global parameters. TODO: Support for multiple schedulers

    def __init__(self, tasks, maintainer_tasks=None, shut_condition=None, min_sleep=0.1, max_sleep=600, parameters=None, name=None):
        """[summary]

        Arguments:
            tasks {[type]} -- [description]

        Keyword Arguments:
            maintain_cond {Condition} -- Condition to kick maintaining on (default: {None})
            shut_cond {[type]} -- Condition to shut down scheduler (default: {None})
        """
        self.tasks = tasks
        self.maintainer_tasks = [] if maintainer_tasks is None else maintainer_tasks
        self.shut_condition = False if shut_condition is None else copy(shut_condition)

        set_statement_defaults(self.shut_condition, _scheduler_=self)

        self.min_sleep = min_sleep
        self.max_sleep = max_sleep

        self.task_returns = Parameters()
        if parameters is not None:
            self.parameters.update(parameters)

        self.name = name if name is not None else id(self)
        self._register_instance()
        
    def _register_instance(self):
        if self.name in _SCHEDULERS:
            raise KeyError(f"All tasks must have unique names. Given: {self.name}. Already specified: {list(_SCHEDULERS.keys())}")
        _SCHEDULERS[self.name] = self

    def __call__(self):
        "Start and run the scheduler"
        exception = None
        try:
            self.setup()

            while not bool(self.shut_condition):

                self.hibernate()
                self.run_cycle()

                self.maintain()
        except SystemExit as exc:
            self.logger.info('Shutting down scheduler.', extra={"action": "shutdown"})
            exception = exc

        except SchedulerRestart as exc:
            self.logger.info('Restart called.', exc_info=True, extra={"action": "shutdown"})
            exception = exc
            self.restart()

        except KeyboardInterrupt as exc:
            self.logger.info('Scheduler interupted. Shutting down scheduler.', exc_info=True, extra={"action": "shutdown"})
            exception = exc

        except Exception as exc:
            self.logger.critical('Scheduler encountered fatal error. Shut down imminent.', exc_info=True, extra={"action": "crash"})
            exception = exc
            raise
        else:
            self.logger.info('Shutting down scheduler.', extra={"action": "shutdown"})
        finally:
            self.shut_down(exception=exception)
# Core
    def setup(self):
        "Set up the scheduler"
        self.logger.info(f"Setting up the scheduler...", extra={"action": "setup"})
        self.n_cycles = 0
        self.startup_time = datetime.datetime.now()

    def hibernate(self):
        "Go to sleep and wake up when next task can be executed"
        delay = self.delay
        self.logger.info(f'Putting scheduler to sleep for {delay} sec', extra={"action": "hibernate"})
        time.sleep(delay)

    def maintain(self):
        """Do maintain work for the scheduler itself
        This could be:
            - Update the task list (ie. if tasks are in a folder and there are new ones)
            - Clean up the log files
            - Update the packages
        """
        self.logger.info(f"Maintaining the scheduler...", extra={"action": "maintain"})
        tasks = self.maintainer_tasks
        if tasks:
            self.logger.info(f"Beginning maintaining cycle. Has {len(tasks)} tasks", extra={"action": "run"})
            for task in tasks:
                if bool(task):
                    self.run_task(task, scheduler=True)
                    if task.force_state is True:
                        # Reset force_state as a run has forced
                        task.force_state = None
    
    def restart(self):
        """Restart the scheduler by creating a new process
        on the temporary run script where the scheduler's is
        process is started.
        """
        # TODO
        # https://stackoverflow.com/a/35874988
        self.logger.info(f"Restarting the scheduler...", extra={"action": "restart"})
        os.execl(sys.executable, sys.executable, *sys.argv)
        sys.exit(0)
    
    def shut_down(self, traceback=None, exception=None):
        """Shut down the scheduler
        This method is meant to controllably close the
        scheduler in case the scheduler crashed (with 
        Python exception) to properly inform the maintainer
        and log the event
        """


    def run_cycle(self):
        "Run a cycle of tasks"
        tasks = self.task_list
        self.logger.info(f"Beginning cycle. Has {len(tasks)} tasks", extra={"action": "run"})
        for task in tasks:
            if bool(task):
                self.run_task(task)
                if task.force_state is True:
                    # Reset force_state as a run has forced
                    task.force_state = None
        self.n_cycles += 1

    def run_task(self, task, scheduler=False):
        "Run/execute one task"
        self.logger.debug(f"Running task {task}")
        
        params = self.parameters | self.task_returns
        start_time = datetime.datetime.now()
        try:
            output = task(**params)
        except Exception as exc:
            exception = exc
            status = "fail"
        else:
            exception = None
            status = "success"
            # Set output to other task to use
            self.task_returns[task.name] = output
        end_time = datetime.datetime.now()

        # TODO: Is there double logging? Task may do it already
        self.log_status(
            task, status, 
            start_time=start_time, end_time=end_time,
            exception=exception
        )


# Logging
    def log_status(self, task, status, **kwargs):
        "Log a run task"

        # Log it to strout/files/email/whatever
        if status == "success":
            self.log_success(task, **kwargs)
        elif status == "fail":
            self.log_failure(task, **kwargs)

    def log_success(self, task, **kwargs):
        "Log a succeeded task"
        self.logger.info(f"Task {task} succeeded.")

    def log_failure(self, task, exception, **kwargs):
        "Log a failed task"
        tb = traceback.format_exception(type(exception), exception, exception.__traceback__)
        tb_string = ''.join(tb)
        self.logger.error(f"Task {task} failed: \n{tb_string}")

# Core properties
    @property
    def delay(self):
        "Number of seconds that needs to be wait for next executable task"
        now = datetime.datetime.now()
        try:
            delay = min(
                task.next_start - now
                for task in self.tasks
            )
        except (AttributeError, ValueError): # Raises ValueError if min() is empty
            delay = 0
        else:
            delay = delay.total_seconds()
        delay = min(max(delay, self.min_sleep), self.max_sleep)
        self.logger.debug(f"Next run cycle at {delay} seconds.")
        return delay

    @property
    def task_list(self):
        now = datetime.datetime.now()
        return sorted(
                self.tasks, 
                key=lambda task: task.priority
            )

    @property
    def maintainer_tasks(self):
        return self._maintainer_tasks

    @maintainer_tasks.setter
    def maintainer_tasks(self, tasks:list):
        for task in tasks:
            task.parameters["_scheduler_"] = self
            set_statement_defaults(task.start_cond, _scheduler_=self)
            
        self._maintainer_tasks = tasks


def _run_task_as_process(task, queue, return_queue, params):
    """Run a task in a separate process (has own memory)"""

    # NOTE: This is in the process and other info in the application
    # cannot be accessed here.
    
    # The task's logger has been removed by MultiScheduler.run_task_as_process
    # (see the method for more info) and we need to recreate the logger now
    # in the actual multiprocessing's process. We only add QueueHandler to the
    # logger (with multiprocessing.Queue as queue) so that all the logging
    # records end up in the main process to be logged properly. 

    # Set the process logger
    
    logger = logging.getLogger(task._logger_basename + "._process") # task._logger_basename
    logger.setLevel(logging.INFO)
    logger.addHandler(
        QueueHandler(queue)
    )
    try:
        with warnings.catch_warnings():
            # task.set_logger will warn that 
            # we do not use two-way logger here 
            # but that is not needed as running 
            # the task itself does not require
            # knowing the status of the task
            # or other tasks
            warnings.simplefilter("ignore")
            task.logger = logger
        #task.logger.addHandler(
        #    logging.StreamHandler(sys.stdout)
        #)
        #task.logger.addHandler(
        #    QueueHandler(queue)
        #)
    except:
        logger.critical(f"Task '{task.name}' crashed in setting up logger.", exc_info=True, extra={"action": "fail", "task_name": task.name})
        raise

    try:
        # NOTE: The parameters are "materialized" 
        # here in the actual process that runs the task
        output = task(**params)
    except Exception as exc:
        # Just catching all exceptions.
        # There is nothing to raise it
        # to :(
        pass
    else:
        return_queue.put((task.name, output))

def _listen_task_status(handlers, queue):
    # TODO: Probably remove
    # https://docs.python.org/3/howto/logging-cookbook.html#logging-to-a-single-file-from-multiple-processes
    logger = logging.getLogger(__name__)
    logger.handlers = handlers
    while True:
        try:
            record = queue.get()
            if record is None:  # We send this as a sentinel to tell the listener to quit.
                break
            logger.handle(record)  # No level or filter logic applied - just do it!
        except Exception:
            import sys, traceback
            print('Whoops! Problem:', file=sys.stderr)
            traceback.print_exc(file=sys.stderr)


class MultiScheduler(Scheduler):
    """Multiprocessing scheduler
    """

    def __init__(self, *args, max_processes=None, timeout="30 minutes", **kwargs):
        super().__init__(*args, **kwargs)
        self.max_processes = cpu_count() if max_processes is None else max_processes

        self.timeout = pd.Timedelta(timeout) if timeout is not None else timeout

    def run_cycle(self):
        "Run a cycle of tasks"
        tasks = self.task_list
        self.logger.info(f"Beginning cycle. Running {len(tasks)} tasks", extra={"action": "run"})
        for task in tasks:
            self.handle_logs()
            self.handle_return()
            if self.is_task_runnable(task):
                # Run the actual task
                self.run_task_as_process(task)
                if task.force_state is True:
                    # Reset force_state as a run has forced
                    task.force_state = None
            elif self.is_timeouted(task):
                # Terminate the task
                self.terminate_task(task, reason="timeout")
            elif self.is_out_of_condition(task):
                # Terminate the task
                self.terminate_task(task)
            pass
        self.n_cycles += 1
        #self.handle_zombie_tasks()

    def run_task_as_process(self, task):
        # TODO: Log that the task is running here as it will take a moment for the task itself to do it
        # (There is a high risk that the task is running twice as the condition did not get the info in time)
        self.logger.debug(f"Running task {task.name}")

        # Multiprocessing's process has its own memory that cause
        # sone issues. Because of this, multiprocessing need to 
        # pickle the parameters passed to the process' function.
        # Issue arises when the logger of a task cannot be pickled
        # due to locks, file buffers etc. in the handlers.
        # To fix this, we need to mirror the task: the task running
        # in the process has its logger removed and the logger
        # is formed in the process function itself (so not passed).

        # The mirror logger just creates and sends all the log records 
        # to the main process (this scheduler) via multiprocessing.Queue
        # and the log records are handled (logged) by the original version 
        # of the task using task.logger.handle(record).

        # Also, the logging records may be best to be handled in the main
        # process anyways: if multiple tasks are writing same log file
        # at the same time, issues may arise.

        proc_task = copy(task)
        params = GLOBAL_PARAMETERS | self.task_returns

        # TODO: set daemon attribute of Process using 1. Task.daemon 2. Scheduler.daemon 3. None
        task._process = Process(target=_run_task_as_process, args=(proc_task, self._log_queue, self._return_queue, params)) 
        # TODO: Pass self._ret_queue to Process (to get the return value of the task)

        task._process.start()
        task._start_time = datetime.datetime.now()

        # There is one more issue to handle: the task must be logged as
        # running before exiting this method (otherwise there is 
        # risk for the task being run multiple times in the same instant
        # as the log about that the task is already running has not yet 
        # arrived). To fix this, we wait till we get approval that the
        # log about that the task is running has arrived and is logged.

        self._handle_next_run_log(task)

        # In case there are others waiting
        self.handle_logs()
        self.handle_return()
    

    def terminate_all(self, reason=None):
        "Terminate all running tasks"
        for task in self.tasks:
            if self.is_alive(task):
                self.terminate_task(task, reason=reason)


    def terminate_task(self, task, reason=None):
        self.logger.debug(f"Terminating task '{task.name}'")
        task._process.terminate()
        # Waiting till the termination is finished. 
        # Otherwise may try to terminate it many times as the process is alive for a brief moment
        task._process.join() 
        task.log_termination(reason=reason)

    def is_timeouted(self, task):
        if not self.is_alive(task):
            return False

        timeout_task = task.timeout
        timeout_sched = self.timeout
        timeout = (
            min(timeout_task, timeout_sched) 
            if timeout_task is not None and timeout_sched is not None
            else timeout_task or timeout_sched
        )
        if timeout is None:
            return False
        run_duration = datetime.datetime.now() - task._start_time
        return run_duration > timeout

    @staticmethod
    def is_alive(task):
        return hasattr(task, "_process") and task._process.is_alive()

    def is_task_runnable(self, task):
        "Whether the task should be run"
        is_not_running = not self.is_alive(task)
        has_free_processors = self.has_free_processors()
        is_condition = bool(task)
        return is_not_running and has_free_processors and is_condition

    def is_out_of_condition(self, task):
        "Whether the task should be terminated"
        is_alive = self.is_alive(task)
        if not is_alive:
            return False
        return bool(task.end_cond) or not bool(task.run_cond)

    def handle_status(self, task):
        "Update task status"
        # TODO: Delete when queue handling is done
        if task._conn.pull(0.01):
            data = task._conn.recv()
            self.log_status(task, **data)
            
    def handle_logs(self, timeout=0.01):
        "Handle the status queue and carries the logging on their behalf"
        queue = self._log_queue
        while True:
            try:
                record = queue.get(block=False)
            except Empty:
                #self.logger.debug(f"Task log queue empty.")
                break
            else:
                self.logger.debug(f"Inserting record for '{record.task_name}' ({record.action})")
                
                if record.action == "fail":
                    # There is a caveat in logging 
                    # https://github.com/python/cpython/blame/fad6af2744c0b022568f7f4a8afc93fed056d4db/Lib/logging/handlers.py#L1383 
                    # https://bugs.python.org/issue34334

                    # The traceback/exception info is no longer in record.exc_info/record.exc_text 
                    # and it has been formatted to record.message/record.msg
                    # This means we have to rely that message really contains
                    # the full traceback

                    record.exc_info = record.message
                    record.exc_text = record.message

                
                task = get_task(record.task_name)
                task.log_record(record)
        # self.parameters.listen()
        # return_values = self._param_queue.get(block=False)
        # self.returns[return_values[0]] = return_values[1]

    def handle_zombie_tasks(self):
        "If there are tasks that has been crashed during setting up the task loggers, this method finds those out and logs them"
        for task in self.tasks:
            if task.status == "run" and not self.is_alive(task):
                task.logger.critical(f"Task '{task.name}' crashed in process setup", extra={"action": "crash"})

    def handle_return(self):
        "Handle task return queue and saves task return values for other tasks to use"
        while True:
            try:
                output = self._return_queue.get(block=False)
                task_name, return_value = output
            except Empty:
                break
            else:
                pass
                # If the return values are to put as GLOBAL_PARAMETERS
                # there should be a maintainer task to take them there
                self.task_returns[task_name] = return_value

    def _handle_next_run_log(self, task):
        "Handle next run log to make sure the task started running before continuing (otherwise may cause accidential multiple launches)"
        action = None
        timeout = 10 # Seconds allowed the setup to take before declaring setup to crash

        queue = self._log_queue
        #record = queue.get(block=True, timeout=None)
        while action != "run":
            try:
                record = queue.get(block=True, timeout=timeout)
            except Empty:
                if not self.is_alive(task):
                    # There will be no "run" log record thus ending the task gracefully
                    task.logger.critical(f"Task '{task.name}' crashed in setup", extra={"action": "fail"})
                    return
            else:
                
                self.logger.debug(f"Inserting record for '{record.task_name}' ({record.action})")
                task = get_task(record.task_name)
                task.log_record(record)

                action = record.action


    def setup(self):
        "Set up the scheduler"
        #self.logger.info(f"Setting up the scheduler...", extra={"action": "setup"})
        #self.setup_listener()
        super().setup()
        self._log_queue = multiprocessing.Queue(-1)
        self._return_queue = multiprocessing.Queue(-1)

    def setup_listener(self):
        # TODO
        handlers = deepcopy(Task.logger.handlers)

        # Set the Task sending the logs to queue instead
        for handler in Task.logger.handlers:
            # All handlers are disabled
            # as they are used in the
            # mirror logger in the listener
            # We cannot remove them because the 2-way logging
            handler.addFilter(FilterAll())

        # Add queue handler which cumulates the records
        # for the listener to consume centrally
        queue = multiprocessing.Queue(-1)
        handler = logging.handlers.QueueHandler(queue)
        Task.logger.addHandler(handler)

        self._task_listener = multiprocessing.Process(
            target=_listen_task_status,
            args=(handlers, queue)
        )
        self._task_listener.start()

    def has_free_processors(self):
        return self.n_alive <= self.max_processes

    @property
    def n_alive(self):
        return sum(self.is_alive(task) for task in self.tasks)

    def shut_down(self, traceback=None, exception=None):
        """Shut down the scheduler
        This method is meant to controllably close the
        scheduler in case the scheduler crashed (with 
        Python exception) to properly inform the maintainer
        and log the event
        """
        if exception is None:
            try:
                # Gracefully shut down (allow remaining tasks to finish)
                while self.n_alive:
                    #time.sleep(self.min_sleep)
                    self.handle_logs()
                    self.handle_return()
                    for task in self.tasks:
                        if self.is_timeouted(task):
                            # Terminate the task
                            self.terminate_task(task, reason="timeout")
                        elif self.is_out_of_condition(task):
                            # Terminate the task
                            self.terminate_task(task)
            except Exception as exc:
                # Fuck it, terminate all
                self.shut_down(exception=exc)
            else:
                self.handle_logs()
                self.handle_return()
        else:
            self.terminate_all(reason="shutdown")
