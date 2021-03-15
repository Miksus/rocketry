


from multiprocessing import Process, cpu_count
import multiprocessing

import traceback
import warnings
import time
import sys, os, subprocess
import logging
from logging.handlers import QueueHandler
import datetime
import platform
from pathlib import Path
from copy import deepcopy, copy
from queue import Empty

import pandas as pd

from atlas.core.task import Task
from atlas.core.log import FilterAll, read_logger

from atlas.core.exceptions import SchedulerRestart

from atlas.core.utils import is_pickleable
from atlas.core.conditions import set_statement_defaults, AlwaysFalse
from atlas.core.parameters import Parameters

# TODO:
#   Allow using return values as parameters to other tasks (new Argument class: Return)
#   Support for Task execution="thread"
#   Unify the supply of parameters
#   New automatically passed parameters:
#       _last_start_, _last_success_, _last_failure_, _task_name_


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
            traceback.print_exc(file=sys.stderr)


class Scheduler:
    """Multiprocessing scheduler

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

    _logger_basename = "atlas.scheduler"

    session = None # This is set as atlas.session

    def __init__(self, session=None, max_processes=None, tasks_as_daemon=True, timeout="30 minutes",
                shut_condition=None, parameters=None,
                min_sleep=0.1, max_sleep=600, 
                logger=None, name=None,
                restarting="replace", 
                instant_shutdown=False):

        # MultiProcessing stuff
        self.max_processes = cpu_count() if max_processes is None else max_processes
        self.tasks_as_daemon = tasks_as_daemon
        self.timeout = pd.Timedelta(timeout) if timeout is not None else timeout

        # Other
        self.session = session or self.session

        self.shut_condition = False if shut_condition is None else copy(shut_condition)
        self.instant_shutdown = instant_shutdown

        set_statement_defaults(self.shut_condition, _scheduler_=self)

        self.min_sleep = min_sleep
        self.max_sleep = max_sleep

        # self.task_returns = Parameters() # TODO

        self.name = name if name is not None else id(self)
        self._register_instance()
        self.logger = logger

        self.restarting = restarting

        if parameters:
            self.session.parameters.update(parameters)

    def _register_instance(self):
        self.session.scheduler = self

    @property
    def tasks(self):
        tasks = self.session.get_tasks()
        # There may be extra rare situation that priority is not in the task
        # for short period if it is being modified thus we use getattr
        return sorted(tasks, key=lambda task: getattr(task, "priority", 0))

    def __call__(self):
        "Start and run the scheduler"
        exception = None
        try:
            self.setup()

            while not bool(self.shut_condition):

                self.hibernate()
                self.run_cycle()

                # self.maintain()
        except SystemExit as exc:
            self.logger.info('Shutting down...', extra={"action": "shutdown"})
            exception = exc

        except SchedulerRestart as exc:
            self.logger.info('Restart called. Shutting down...', exc_info=True, extra={"action": "shutdown"})
            exception = exc

        except KeyboardInterrupt as exc:
            self.logger.info('Interupted. Shutting down...', exc_info=True, extra={"action": "shutdown"})
            exception = exc

        except Exception as exc:
            self.logger.critical('Fatal error encountered. Shutting down...', exc_info=True, extra={"action": "crash"})
            exception = exc
            raise
        else:
            self.logger.info('Purpose completed. Shutting down...', extra={"action": "shutdown"})
        finally:
            self.shut_down(exception=exception)

    def run_cycle(self):
        "Run a cycle of tasks"
        tasks = self.tasks
        self.logger.debug(f"Beginning cycle. Running {len(tasks)} tasks...", extra={"action": "run"})
        for task in tasks:
            with task.lock:
                self.handle_logs()
                self.handle_return()
                if task.on_startup or task.on_shutdown:
                    # Startup or shutdown tasks are not run in main sequence
                    pass
                elif self.is_task_runnable(task):
                    # Run the actual task
                    self.run_task(task)
                    # Reset force_run as a run has forced
                    task.force_run = False
                elif self.is_timeouted(task):
                    # Terminate the task
                    self.terminate_task(task, reason="timeout")
                elif self.is_out_of_condition(task):
                    # Terminate the task
                    self.terminate_task(task)

        self.n_cycles += 1
        #self.handle_zombie_tasks()
        

    def run_task(self, task, *args, extra_params=None, **kwargs):
        params = self.session.parameters
        extra_params = {} if extra_params is None else extra_params
        params = params | Parameters(_scheduler_=self, _task_=task) | Parameters(**extra_params)
        start_time = datetime.datetime.now()
        try:
            task(
                params=params, 
                # Additional arguments if multiprocessing
                log_queue=self._log_queue, 
                return_queue=self._return_queue, 
                daemon=self.tasks_as_daemon
            )
        except SchedulerRestart as exc:
            raise 
        except Exception as exc:
            exception = exc
            status = "fail"
        else:
            exception = None
            status = "success"
            # Set output to other task to use
            # self.task_returns[task.name] = output
        end_time = datetime.datetime.now()

        # NOTE: This only logs to the scheduler (task logger already handled). Probably remove this.
        self.log_status(
            task, status, 
            start_time=start_time, end_time=end_time,
            exception=exception
        )

    def terminate_all(self, reason=None):
        "Terminate all running tasks"
        for task in self.tasks:
            if task.is_alive():
                self.terminate_task(task, reason=reason)

    def terminate_task(self, task, reason=None):
        self.logger.debug(f"Terminating task '{task.name}'")
        is_threaded = hasattr(task, "_thread")
        is_multiprocessed = hasattr(task, "_process")
        if task.is_alive_as_thread():
            # We can only kindly ask the thread to...
            # get the fuck out please.
            task.thread_terminate.set()

        elif task.is_alive_as_process():
            task._process.terminate()
            # Waiting till the termination is finished. 
            # Otherwise may try to terminate it many times as the process is alive for a brief moment
            task._process.join() 
            task.log_termination(reason=reason)

            # Resetting attr force_termination
            task.force_termination = False
        else:
            # The process/thread probably just died after the check
            pass

    def is_timeouted(self, task):
        if not hasattr(task, "_thread") and not hasattr(task, "_process"):
            # Task running on the main process
            # cannot be left running
            return False
        elif not task.is_alive():
            return False

        timeout = (
            task.timeout if task.timeout is not None
            else self.timeout
        )
        
        if timeout is None:
            return False
        run_duration = datetime.datetime.now() - task.start_time
        return run_duration > timeout

    def is_task_runnable(self, task):
        "Whether the task should be run"
        if task.execution == "process":
            is_not_running = not task.is_alive()
            has_free_processors = self.has_free_processors()
            is_condition = bool(task)
            return is_not_running and has_free_processors and is_condition
        elif task.execution == "main":
            is_condition = bool(task)
            return is_condition
        elif task.execution == "thread":
            is_not_running = not task.is_alive()
            is_condition = bool(task)
            return is_not_running and is_condition
        else:
            raise NotImplementedError(task.execution)

    def is_out_of_condition(self, task):
        "Whether the task should be terminated"
        if not task.is_alive():
            # NOTE:
            # Task running on the main process
            # cannot be left running
            return False

        elif task.force_termination:
            return True

        else:
            return bool(task.end_cond) or not bool(task.run_cond)
            
    def handle_logs(self, timeout=0.01):
        "Handle the status queue and carries the logging on their behalf"
        # TODO: This could be maybe done in the tasks
        queue = self._log_queue
        while True:
            try:
                record = queue.get(block=False)
            except Empty:
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

                    record.exc_info = record.exc_text
                    record.exc_text = record.exc_text
                    if record.exc_text is not None and record.exc_text not in record.message:
                        record.message = record.message + "\n" + record.message

                
                task = self.session.get_task(record.task_name)
                task.log_record(record)
        # return_values = self._param_queue.get(block=False)
        # self.returns[return_values[0]] = return_values[1]

    def handle_zombie_tasks(self):
        "If there are tasks that has been crashed during setting up the task loggers, this method finds those out and logs them"
        for task in self.tasks:
            if task.status == "run" and not task.is_alive():
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
                # If the return values are to put as
                # there should be a maintainer task to take them there
                #self.task_returns[task_name] = return_value

    def hibernate(self):
        "Go to sleep and wake up when next task can be executed"
        delay = self.delay
        self.logger.debug(f'Putting scheduler to sleep for {delay} sec', extra={"action": "hibernate"})
        time.sleep(delay)

    def setup(self):
        "Set up the scheduler"
        #self.setup_listener()
        self.logger.info(f"Setting up...", extra={"action": "setup"})

        self._log_queue = multiprocessing.Queue(-1)
        self._return_queue = multiprocessing.Queue(-1)

        self.n_cycles = 0
        self.startup_time = datetime.datetime.now()

        self.logger.info(f"Beginning startup sequence...")
        for task in self.tasks:
            if task.on_startup:
                if isinstance(task.start_cond, AlwaysFalse) and not task.disabled: 
                    # Make sure the tasks run if start_cond not set
                    task.force_run = True

                if self.is_task_runnable(task):
                    self.run_task(task)

        self.logger.info(f"Setup complete.")

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
        return sum(task.is_alive() for task in self.tasks)

    def shut_down_processes(self, traceback=None, exception=None):
        non_fatal_excs = (SchedulerRestart,) # Exceptions that are allowed to have graceful exit
        wait_for_finish = not self.instant_shutdown and (exception is None or isinstance(exception, non_fatal_excs))
        if wait_for_finish:
            try:
                # Gracefully shut down (allow remaining tasks to finish)
                while self.n_alive:
                    #time.sleep(self.min_sleep)
                    self.handle_logs()
                    self.handle_return()
                    for task in self.tasks:
                        if task.permanent_task:
                            # Would never "finish" anyways
                            self.terminate_task(task)
                        elif self.is_timeouted(task):
                            # Terminate the task
                            self.terminate_task(task, reason="timeout")
                        elif self.is_out_of_condition(task):
                            # Terminate the task
                            self.terminate_task(task)
            except Exception as exc:
                # Fuck it, terminate all
                self.shut_down_processes(exception=exc)
                return
            else:
                self.handle_logs()
                self.handle_return()
        else:
            self.terminate_all(reason="shutdown")

    def shut_down(self, traceback=None, exception=None):
        """Shut down the scheduler
        This method is meant to controllably close the
        scheduler in case the scheduler crashed (with 
        Python exception) to properly inform the maintainer
        and log the event.

        Also responsible of restarting the scheduler if
        ordered.
        """
        
        self.logger.info(f"Beginning shutdown sequence...")
        # Make sure the tasks run if start_cond not set
        for task in self.tasks:
            if task.on_shutdown:

                if isinstance(task.start_cond, AlwaysFalse) and not task.disabled: 
                    # Make sure the tasks run if start_cond not set
                    task.force_run = True

                if self.is_task_runnable(task):
                    self.run_task(task)

        self.logger.info(f"Shutting down tasks...")
        self.shut_down_processes(traceback, exception)

        self.logger.info(f"Shutdown completed. Good bye.")
        if isinstance(exception, SchedulerRestart):
            # Clean up finished, restart is finally
            # possible
            self.restart()

    def restart(self):
        """Restart the scheduler by creating a new process
        on the temporary run script where the scheduler's is
        process is started.
        """
        # TODO
        # https://stackoverflow.com/a/35874988
        self.logger.debug(f"Restarting...", extra={"action": "restart"})
        python = sys.executable

        if self.restarting == "replace":
            os.execl(python, python, *sys.argv)
            # After here no code will be run
        elif self.restarting == "relaunch":
            # Relaunch the process
            subprocess.Popen([python, *sys.argv], shell=False, close_fds=True)
        elif self.restarting == "fresh":
            # Relaunch the process in new window
            if platform.system() == "Windows":
                subprocess.Popen([python, *sys.argv], shell=False, close_fds=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                # Linux does not have CREATE_NEW_CONSOLE creation flag but shell=True is pretty close
                subprocess.Popen([python, *sys.argv], shell=True, close_fds=True)
        else:
            raise ValueError(f"Invalid restaring: {self.restarting}")

    @property
    def delay(self):
        # TODO: Delete
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


# Logging
    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, logger):
        if logger is None:
            # Get class logger (default logger)
            logger = logging.getLogger(self._logger_basename)

        if not logger.name.startswith(self._logger_basename):
            raise ValueError(f"Logger name must start with '{self._logger_basename}' as session finds loggers with names")

        # TODO: Use TaskAdapter to relay the scheduler name?
        self._logger = logger

    def log_status(self, task, status, **kwargs):
        "Log a run task"

        # Log it to strout/files/email/whatever
        if status == "success":
            self.log_success(task, **kwargs)
        elif status == "fail":
            self.log_failure(task, **kwargs)

    def log_success(self, task, **kwargs):
        "Log a succeeded task"
        self.logger.debug(f"Task {task} succeeded.")

    def log_failure(self, task, exception, **kwargs):
        "Log a failed task"
        tb = traceback.format_exception(type(exception), exception, exception.__traceback__)
        tb_string = ''.join(tb)
        self.logger.debug(f"Task {task} failed: \n{tb_string}")