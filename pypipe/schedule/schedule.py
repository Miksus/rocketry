


from multiprocessing import Process, cpu_count
import multiprocessing

import traceback
import warnings
import time
import sys
import logging
from logging.handlers import QueueHandler
import datetime
from pathlib import Path
from copy import deepcopy, copy
from queue import Empty

from pypipe.task.base import Task, get_task
from pypipe.task import ScriptTask, JupyterTask, FuncTask, CommandTask
from pypipe.log import FilterAll, read_logger

from .exceptions import SchedulerRestart

from pypipe.utils import is_pickleable
from pypipe.conditions import set_statement_defaults
from pypipe.parameters import Parameters

# TODO: Controlled crashing
#   Wrap __call__ with a decor that has try except

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

    logger = logging.getLogger(__name__)

    def __init__(self, tasks, maintain_tasks=None, shut_condition=None, min_sleep=0.1, max_sleep=600, parameters=None):
        """[summary]

        Arguments:
            tasks {[type]} -- [description]

        Keyword Arguments:
            maintain_cond {Condition} -- Condition to kick maintaining on (default: {None})
            shut_cond {[type]} -- Condition to shut down scheduler (default: {None})
        """
        self.tasks = tasks
        self.maintain_tasks = [] if maintain_tasks is None else maintain_tasks
        self.shut_condition = False if shut_condition is None else shut_condition

        self.shut_condition = set_statement_defaults(self.shut_condition, scheduler=self)

        for maintain_task in self.maintain_tasks:
            maintain_task.start_cond = set_statement_defaults(maintain_task.start_cond, scheduler=self)
            maintain_task.groups = ("maintain",)
            maintain_task.set_logger() # Resetting the logger as group changed

        self.variable_params = {}
        self.fixed_params = {}

        self.min_sleep = min_sleep
        self.max_sleep = max_sleep

        self.parameters = Parameters() if parameters is None else Parameters

    @staticmethod
    def set_default_logger(logger):
        # Emptying existing handlers
        if logger is None:
            logger = __name__
        elif isinstance(logger, str):
            logger = logging.getLogger(logger)

        logger.handlers = []

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

        logger.addHandler(handler)

    def __call__(self):
        "Start and run the scheduler"
        exception = None
        try:
            self.setup()

            while not bool(self.shut_condition):

                self.hibernate()
                self.run_cycle()

                self.maintain()

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
        tasks = self.maintain_tasks
        if tasks:
            self.logger.info(f"Beginning maintaining cycle. Has {len(tasks)} tasks", extra={"action": "run"})
            for task in tasks:
                if bool(task):
                    self.run_task(task, scheduler=True)
    
    def restart(self):
        """Restart the scheduler by creating a new process
        on the temporary run script where the scheduler's is
        process is started.
        """
        # TODO
        # https://stackoverflow.com/a/35874988
        self.logger.info(f"Restarting the scheduler...", extra={"action": "restart"})
        subprocess.call(["bash", "restart_scheduler.sh"])
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
                task.force_run = False
        self.n_cycles += 1

    def run_task(self, task, scheduler=False):
        "Run/execute one task"
        self.logger.debug(f"Running task {task}")
        
        start_time = datetime.datetime.now()
        try:
            params = self.parameters[task]
            task(**params)
        except Exception as exc:
            exception = exc
            status = "fail"
        else:
            exception = None
            status = "success"
        end_time = datetime.datetime.now()

        # TODO: Is there double logging? Task may do it already
        self.log_status(
            task, status, 
            start_time=start_time, end_time=end_time,
            exception=exception
        )

    def get_params(self, scheduler):
        variable_params = {key: val() for key, val in self.variable_params.items()}
        params = {**variable_params, **self.fixed_params}
        if scheduler:
            params["scheduler"] = self
        return params
        

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

    def get_history(self, group_name=None):
        logger = Task.get_logger(group_name=group_name)
        return read_logger(logger)

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
                key=lambda task: (
                    task.priority, 
                    task.start_cond.estimate_timedelta(now)
                    if hasattr(task.start_cond, "estimate_timedelta")
                    else datetime.timedelta.resolution
                )
            )

# Factory
    @classmethod
    def from_folder(cls, path, include_main=True, include_ipynb=True, **kwargs):
        root = Path(path)
        # TODO: Probably better to delete for now
        tasks = []
        if include_main:
            for file in root.glob('**/main.py'):
                if file.is_file():
                    

                    relative_path = Path(*file.parts[len(root.parts):]) # Removed beginning, C://myuser/...

                    group = '.'.join(relative_path.parts[:-2]) # All but the mytask/main.py
                    name = '.'.join(relative_path.parts[:-1]) # All but the main.py
                    task = ScriptTask.from_file(file, name=name, group=group) # Figures the conditions etc.
                    tasks.append(task)

        if include_ipynb:
            for file in path.glob('**/*.ipynb'):
                if file.is_file():
                    relative_path = Path(*file.parts[len(root.parts):]) # Removed beginning, C://myuser/...
                    name = '.'.join(relative_path.parts).replace(".ipynb", "") # All but the main.py
                    task = NotebookTask.from_file(file, name=name)
                    tasks.append(task)

        return cls(tasks, **kwargs)



def _run_task_as_process(task, queue, params):
    """Run a task in a separate process (has own memory)"""

    # NOTE: This is in the process and other info in the application
    # cannot be accessed here.
    
    # The task's logger has been removed by MultiScheduler.run_task_as_process
    # (see the method for more info) and we need to recreate the logger now
    # in the actual multiprocessing's process. We only add QueueHandler to the
    # logger (with multiprocessing.Queue as queue) so that all the logging
    # records end up in the main process to be logged properly. 

    # Set the process logger
    logger = logging.getLogger("pypipe.schedule.process")
    logger.setLevel(logging.INFO)

    with warnings.catch_warnings():
        # task.set_logger will warn that 
        # we do not use two-way logger here 
        # but that is not needed as running 
        # the task itself does not require
        # knowing the status of the task
        # or other tasks
        warnings.simplefilter("ignore")
        task.set_logger(logger)
    #task.logger.addHandler(
    #    logging.StreamHandler(sys.stdout)
    #)
    task.logger.addHandler(
        QueueHandler(queue)
    )


    try:
        task(**params)
    except Exception as exc:
        # Just catching all exceptions.
        # There is nothing to raise it
        # to :(
        pass

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

    timeout = datetime.timedelta(0, 30*60)

    def __init__(self, *args, max_processes=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_processes = cpu_count() if max_processes is None else max_processes


    def run_cycle(self):
        "Run a cycle of tasks"
        tasks = self.task_list
        self.logger.info(f"Beginning cycle. Running {len(tasks)} tasks", extra={"action": "run"})
        for task in tasks:
            self.handle_logs()
            if self.is_task_runnable(task):
                # Run the actual task
                self.run_task_as_process(task)
                task.force_run = False
            elif self.is_timeouted(task):
                # Terminate the task
                self.terminate_task(task, reason="timeout")
            elif self.is_out_of_condition(task):
                # Terminate the task
                self.terminate_task(task)
        self.n_cycles += 1

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
        proc_task.logger = None
        proc_task.start_cond = None
        proc_task._execution_condition = None
        proc_task._dependency_condition = None

        params = self.parameters[task]
        params.remove_unpicklable()

        #child_pipe, parent_pipe = multiprocessing.Pipe() # Make 2 way connection
        #process = Process(target=_run_task_as_process, args=(proc_task, self._log_queue, self.get_params(only_picleable=True)))
        #task._processes.append(process)
        task._process = Process(target=_run_task_as_process, args=(proc_task, self._log_queue, params))
        #task._conn = parent_pipe

        task._process.start()
        task._start_time = datetime.datetime.now()

        # There is one more issue to handle: the task must be logged as
        # running before exiting this method (otherwise there is 
        # risk for the task being run multiple times in the same instant
        # as the log about that the task is already running has not yet 
        # arrived). To fix this, we wait till we get approval that the
        # log about that the task is running has arrived and is logged.

        self.handle_next_run_log()

        # In case there are others waiting
        self.handle_logs()
        

    def get_params(self, only_picleable=False, scheduler=False):
        variable_params = {key: val() for key, val in self.variable_params.items()}
        params = {**variable_params, **self.fixed_params}
        if only_picleable:
            params = {key:val for key, val in params.items() if is_pickleable(val)}
        if scheduler:
            params["scheduler"] = self
        return params

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

        timeout = task.timeout
        if timeout is None:
            return False
        run_time = datetime.datetime.now() - task._start_time
        run_time_seconds = run_time.total_seconds()
        return run_time_seconds > timeout

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
                record = queue.get(timeout=timeout)
            except Empty:
                self.logger.debug(f"Task log queue empty.")
                break
            else:
                self.logger.debug(f"Inserting record for '{record.task_name}' ({record.action})")
                task = get_task(record.task_name)
                task.log_record(record)

    def handle_next_run_log(self):
        "Handle next run log to make sure the task started running before continuing (otherwise may cause accidential multiple launches)"
        action = None
        while action != "run":
            queue = self._log_queue
            record = queue.get()


            self.logger.debug(f"Inserting record for' {record.task_name}' ({record.action})")
            task = get_task(record.task_name)
            task.log_record(record)
            action = record.action

    def setup(self):
        "Set up the scheduler"
        #self.logger.info(f"Setting up the scheduler...", extra={"action": "setup"})
        #self.setup_listener()
        super().setup()
        self._log_queue = multiprocessing.Queue(-1)

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
        print(exception)
        try:
            if exception is None:
                while self.n_alive:
                    #time.sleep(self.min_sleep)
                    self.handle_logs()
                    for task in self.tasks:
                        if self.is_timeouted(task):
                            # Terminate the task
                            self.terminate_task(task, reason="timeout")
                        elif self.is_out_of_condition(task):
                            # Terminate the task
                            self.terminate_task(task)
            else:
                self.terminate_all(reason="shutdown")
        except Exception as exc:
            self.shut_down(exception=exc)
        else:
            self.handle_logs()