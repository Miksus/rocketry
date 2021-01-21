
from atlas.core.task import Task

import os, sys

class Restart(Task):
    "Restart the scheduler"

    def execute_action(self, argv=None, exit=True, **kwargs):
        if argv is None:
            argv = sys.argv
        # Works on Windows at least:
        os.execl(sys.executable, sys.executable, *sys.argv)
        if exit:
            sys.exit()