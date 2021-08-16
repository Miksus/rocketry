
class ScheduerInterupt(Exception):
    "Close the scheduler"

class SchedulerRestart(Exception):
    "Restart the scheduler"

class CycleInterupt(Exception):
    "Stop executing the current cycle"

class TaskInactionException(Exception):
    "Task did not succeed nor fail. It did not need to run."

class TaskDisableException(Exception):
    "Disable the task. Considered as failure."

class TaskTerminationException(Exception):
    """Task was terminated.
    This should only be raised by threaded
    tasks to signal that they did indeed
    listen the thread_please_terminate event
    and ended as a result of that"""