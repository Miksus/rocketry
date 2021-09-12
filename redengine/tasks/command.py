

from redengine.core.task import Task
#from .config import parse_config

from pathlib import Path
import inspect
import importlib
import subprocess
import re


class CommandTask(Task):
    """Task that executes a command from 
    shell/terminal
    """
    timeout = None

    def __init__(self, command=None, cwd=None, shell=False, capture_output=True, executable=None, **kwargs):
        self.action = command
        super().__init__(**kwargs)
        self.kwargs_popen = {"cwd": cwd, "shell":shell, "executable": executable}#, "capture_output": capture_output}
        # About shell: https://stackoverflow.com/a/36299483/13696660

    def execute_action(self, **parameters):

        # args, kwargs = parameters.materialize()
        command = self.action

        # TODO: kwargs to parameters, ie.
        # {"x": 123, "y": "a value"} --> "-x 123", "-y 'a value'"

        # command = [command] + list(args) if isinstance(command, str) else command + list(args)
        # command can be: "myfile.bat", "echo Hello!" or ["python", "v"]
        # https://stackoverflow.com/a/5469427/13696660
        pipe = subprocess.Popen(command,
                                #shell=True,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                **self.kwargs_popen
                                )
        try:
            outs, errs = pipe.communicate(timeout=self.timeout)
        except subprocess.TimeoutExpired:
            # https://docs.python.org/3.3/library/subprocess.html#subprocess.Popen.communicate
            pipe.kill()
            outs, errs = pipe.communicate()
            raise
        
        return_code = pipe.returncode
        if return_code != 0:
            if hasattr(errs, "decode"):
                errs = errs.decode("utf-8", errors="ignore")
            raise OSError(f"Failed running command ({return_code}): \n{errs}")
        return outs

    def get_default_name(self):
        command = self.action
        return command if isinstance(command, str) else ' '.join(command)

