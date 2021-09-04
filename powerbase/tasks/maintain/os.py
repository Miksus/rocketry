
from powerbase.core.task import Task
from powerbase.core.exceptions import SchedulerRestart, SchedulerExit


class Restart(Task):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.execution = "main"

    def execute_action(self, **kwargs):
        raise SchedulerRestart()

    def get_default_name(self):
        return "restart"


class ShutDown(Task):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.execution = "main"

    def execute_action(self, **kwargs):
        raise SchedulerExit()

    def get_default_name(self):
        return "shutdown"