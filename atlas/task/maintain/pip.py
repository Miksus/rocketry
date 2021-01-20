
from atlas.core.task import Task

import sys
import subprocess

class PipInstall(Task):
    def execute_action(self, 
                        interpreter=None, 
                        requirements=None, packages=None, 
                        options=None,
                        **kwargs):
                        
        if interpreter is None:
            interpreter = sys.executable
        if requirements is None and packages is None:
            requirements = "requirements.txt"

        pip_install = [interpreter, "-m", "pip", "install"]
        options = [] if options is None else options
        # https://pip.pypa.io/en/stable/reference/pip_install/#install-requirement

        # TODO: https://stackoverflow.com/a/27254355/13696660
        if packages is not None:
            subprocess.check_call(pip_install + options + packages)
        else: 
            subprocess.check_call(pip_install + options + ["-r", requirements])