
import sys
from pathlib import Path
import subprocess

from redengine.core.task import Task


class PipInstall(Task):

    # Note: __init__ contains task specific params and execute session specific
    def __init__(self, requirements=None, package=None, options=None, **kwargs):
        self.requirements = requirements
        self.packages = [package] if isinstance(package, str) else package
        self.options = options
        super().__init__(**kwargs)

    def execute(self, interpreter=None, root=None, **kwargs):
                        
        if interpreter is None:
            interpreter = sys.executable
        requirements = self.requirements
        if requirements is None and self.packages is None:
            # Use default requirements.txt from root
            requirements = str(Path(root) / "requirements.txt")

        pip_install = [interpreter, "-m", "pip", "install"]
        options = [] if self.options is None else self.options
        # https://pip.pypa.io/en/stable/reference/pip_install/#install-requirement

        # TODO: https://stackoverflow.com/a/27254355/13696660
        if self.packages is not None:
            subprocess.check_call(pip_install + options + self.packages)
        else: 
            # Install from requirements file
            requirements_txt = requirements
            subprocess.check_call(pip_install + options + ["-r", requirements_txt])