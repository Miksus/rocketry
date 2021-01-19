
from atlas.core.task import Task

import os, sys

class Restart(Task):
    "Restart the scheduler"

    def execute_action(self, argv=None):
        if argv is None:
            argv = sys.argv
        os.execv(sys.argv[0], sys.argv)