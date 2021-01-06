


class ScheduerInterupt(Exception):
    "Close the scheduler"

class SchedulerRestart(Exception):
    "Restart the scheduler"

class CycleInterupt(Exception):
    "Stop executing the current cycle"