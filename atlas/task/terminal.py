

from atlas.core.task import Task, register_task_cls
#from .config import parse_config

from pathlib import Path
import inspect
import importlib
import subprocess
import re

@register_task_cls
class CommandTask(Task):
    """Task that executes a commandline command
    """
    timeout = None

    def __init__(self, *args, cwd=None, shell=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs_popen = {"cwd": cwd, "shell":shell}
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
                                capture_output=True,
                                #stdin=subprocess.PIPE,
                                #stdout=subprocess.PIPE,
                                #stderr=subprocess.PIPE,
                                **self.kwargs_popen
                                )
        try:
            outs, errs = pipe.communicate(timeout=self.timeout)
        except subprocess.TimeoutExpired:
            # https://docs.python.org/3.3/library/subprocess.html#subprocess.Popen.communicate
            pipe.kill()
            outs, errs = pipe.communicate()
            raise
        
        if pipe.returncode != 0:
            errs = errs.decode("utf-8", errors="ignore")
            raise OSError(f"Failed running command: \n{errs}")
        return outs

    def get_default_name(self):
        command = self.action
        return command if isinstance(command, str) else ' '.join(command)

    @classmethod
    def from_folder(cls, path):
        "get all tasks from folder"
        root = Path(path)

        types = ("**/*.bat", "**/*.sh")

        tasks = []
        for type_ in types:
            for file in root.glob(type_):
                tasks.append(cls.from_file(file)) 
        return tasks

