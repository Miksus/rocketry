
# Extensions for tasks
import re
from redengine.core import Task

class MyTask(Task):
    """My Task class"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def execute(self, *args, **kwargs):
        # # What the task executes.
        pass