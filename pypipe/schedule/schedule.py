


from multiprocessing import Process, cpu_count
import multiprocessing

import traceback
import time
import sys
import logging
from logging.handlers import QueueHandler
import datetime
from pathlib import Path
from copy import deepcopy, copy
from queue import Empty

from .task import Task, get_task
from pypipe.log import FilterAll

# TODO: Controlled crashing
#   Wrap __call__ with a decor that has try except

class Scheduler:
    """
    Simple Scheduler 
    """

    logger = logging.getLogger(__name__)

    shortest_sleep = 5
    longest_sleep = 10 * 60

    def __init__(self, tasks, maintain_condition=None, shut_condition=None):
        """[summary]

        Arguments:
            tasks {[type]} -- [description]

        Keyword Arguments:
            maintain_cond {Condition} -- Condition to kick maintaining on (default: {None})
            shut_cond {[type]} -- Condition to shut down scheduler (default: {None})
        """
        self.tasks = tasks
        self.maintain_condition = True if maintain_condition is None else maintain_condition
        self.shut_condition = False if shut_condition is None else shut_condition

    def __call__(self):
        "Start and run the scheduler"
        try:
            self.setup()

            while not bool(self.shut_condition):

                self.hibernate()
                self.run_cycle()

                if bool(self.maintain_condition):
                    self.maintain()

        except KeyboardInterrupt as exc:
            self.logger.info('Scheduler interupted. Shutting down scheduler.', exc_info=True, extra={"action": "shutdown"})
            exception = exc

        except Exception as exc:
            self.logger.critical('Scheduler encountered fatal error. Shut down imminent.', exc_info=True, extra={"action": "crash"})
            exception = exc
            raise
        else:
            self.logger.info('Shutting down scheduler.', extra={"action": "shutdown"})
            exception = None
        finally:
            self.shut_down(exception=exception)
# Core
    def setup(self):
        "Set up the scheduler"
        self.logger.info(f"Setting up the scheduler...", extra={"action": "setup"})

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
        self.logger.info(f"Beginning cycle. Running {len(tasks)} tasks", extra={"action": "run"})
        for task in tasks:
            if bool(task.start_cond):
                self.run_task(task)

    def run_task(self, task):
        "Run/execute one task"
        self.logger.debug(f"Running task {task}")
        
        start_time = datetime.datetime.now()
        try:
            task()
        except Exception as exc:
            exception = exc
            status = "fail"
        else:
            exception = None
            status = "success"
        end_time = datetime.datetime.now()

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
                task.start_cond.estimate_timedelta(now).total_seconds()
                for task in self.tasks
            )
        except AttributeError:
            delay = 0
        self.logger.debug(f"Next run cycle at {delay} seconds.")
        return min(max(delay, self.shortest_sleep), self.longest_sleep)

    @property
    def task_list(self):
        now = datetime.datetime.now()
        return sorted(
                self.tasks, 
                key=lambda task: (
                    task.priority, 
                    task.start_cond.estimate_timedelta(now)
                    if hasattr(task.start_cond, "estimate_timedelta")
                    else 0
                )
            )

# Factory
    @classmethod
    def from_folder(cls, path):
        path = Path(path)

        tasks = []
        for file in path.glob('**/main.py'):
            if file.is_file():
                task = Task.from_file(file, name=str(file).replace(r'/main.py', ''))
                tasks.append(task)
        return cls(tasks)



def _run_task_as_process(task, queue):
    "Run a task in a separate process (has own memory)"
    # TODO: set the queue here, make again the logger to the task and add QueueHandler to the logger

    task.set_logger(logging.getLogger("pypipe.schedule.process"))

    task.logger.addHandler(
        logging.StreamHandler(sys.stdout)
    )
    task.logger.addHandler(
        QueueHandler(queue)
    )


    try:
        task()
    except Exception as exc:
        exception = exc
        status = "fail"
    else:
        status = "success"
    #conn.send({"status": task.status, "end_time": datetime.datetime.now()})

def _listen_task_status(handlers, queue):
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
                self.run_task(task)
            elif self.is_task_killable(task):
                # Terminate the task
                self.terminate_task(task)

    def run_task(self, task):
        # TODO: Log that the task is running here as it will take a moment for the task itself to do it
        # (There is a high risk that the task is running twice as the condition did not get the info in time)
        self.logger.debug(f"Running task {task.name}")
        #task.log_running()
        # Multiprocessing pickles the task but the logger in a task
        # cannot be pickled due to locks etc. We circumvent this by
        # copying the task without the logger
        proc_task = copy(task)
        proc_task.logger = None
        proc_task.start_cond = None

        #child_pipe, parent_pipe = multiprocessing.Pipe() # Make 2 way connection
        task._process = Process(target=_run_task_as_process, args=(proc_task, self._log_queue,))
        #task._conn = parent_pipe

        task._process.start()
        task._start_time = datetime.datetime.now()
        self.handle_next_log()
        # In case there are others waiting
        self.handle_logs()

    def terminate_task(self, task):
        self.logger.debug(f"Terminating task {task.name}")
        task._process.terminate()

    def is_timeouted(self, task):
        timeout = task.timeout
        if timeout is None:
            return False
        run_time = task._start_time - datetime.datetime.now()
        return run_time > timeout

    @staticmethod
    def is_alive(task):
        return hasattr(task, "_process") and task._process.is_alive()

    def is_task_runnable(self, task):
        "Whether the task should be run"
        is_not_running = not self.is_alive(task)
        has_free_processors = self.has_free_processors()
        is_condition = bool(task.start_cond)
        return is_not_running and has_free_processors and is_condition

    def is_task_killable(self, task):
        "Whether the task should be terminated"
        is_alive = self.is_alive(task)
        is_overtime = self.is_timeouted(task)
        is_within_condition = bool(task.end_cond) or not bool(task.run_cond)
        return is_alive and (is_overtime or is_within_condition)

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
                self.logger.debug(f"Inserting record for {record.task_name} ({record.action})")
                task = get_task(record.task_name)
                task.logger.handle(record)

    def handle_next_log(self):
        "Handle the status queue and carries the logging on their behalf"
        queue = self._log_queue
        record = queue.get()

        self.logger.debug(f"Inserting record for {record.task_name} ({record.action})")
        task = get_task(record.task_name)
        task.logger.handle(record)

    def setup(self):
        "Set up the scheduler"
        self.logger.info(f"Setting up the scheduler...", extra={"action": "setup"})
        #self.setup_listener()
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