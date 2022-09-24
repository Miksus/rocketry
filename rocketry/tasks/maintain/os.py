
from rocketry.core.task import Task
from rocketry.exc import SchedulerRestart, SchedulerExit


class Restart(Task):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.execution = "main"

    def execute(self, **kwargs):
        raise SchedulerRestart()

    def get_default_name(self, **kwargs):
        return "restart"


class ShutDown(Task):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.execution = "main"

    def execute(self, **kwargs):
        raise SchedulerExit()

    def get_default_name(self, **kwargs):
        return "shutdown"
