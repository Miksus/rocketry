
from atlas.core.task import Task
from atlas.core.schedule.exceptions import SchedulerRestart

import os, sys, subprocess

class Restart(Task):
    "Restart the scheduler"

    def execute_action(self, **kwargs):
        raise SchedulerRestart(**kwargs)