
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