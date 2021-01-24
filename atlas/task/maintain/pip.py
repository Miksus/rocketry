
from atlas.core.task import Task

import sys
from pathlib import Path
import subprocess

class PipInstall(Task):
    def execute_action(self, 
                        interpreter=None, 
                        root=None,
                        requirements=None, 
                        packages=None, 
                        options=None,
                        **kwargs):
                        
        if interpreter is None:
            interpreter = sys.executable
        if requirements is None and packages is None:
            requirement_txt = str(Path(root) / "requirements.txt")

        pip_install = [interpreter, "-m", "pip", "install"]
        options = [] if options is None else options
        # https://pip.pypa.io/en/stable/reference/pip_install/#install-requirement

        # TODO: https://stackoverflow.com/a/27254355/13696660
        if packages is not None:
            subprocess.check_call(pip_install + options + packages)
        else: 
            # Install from requirements file
            subprocess.check_call(pip_install + options + ["-r", requirement_txt])