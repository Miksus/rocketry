
from atlas.core.task import Task, register_task_cls
from atlas.core.exceptions import SchedulerRestart

import os, sys, subprocess

@register_task_cls
class Restart(Task):
    "Restart the scheduler"

    def execute_action(self, **kwargs):
        raise SchedulerRestart(**kwargs)