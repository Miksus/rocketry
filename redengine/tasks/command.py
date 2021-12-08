
import subprocess
import warnings

from redengine.core.parameters.parameters import Parameters
from redengine.core.task import Task


class CommandTask(Task):
    """Task that executes a command from 
    shell/terminal.

    Parameters
    ----------
    command : str, list
        Command to execute.
    cwd : str, optional
        Sets the current directory before the child is executed.
    shell : bool, optional
        If true, the command will be executed through the shell.
    kwds_popen : dict, optional
        Keyword arguments to be passed to subprocess.Popen
    **kwargs : dict
        See :py:class:`redengine.core.Task`

    Examples
    --------

    >>> from redengine.tasks import CommandTask
    >>> task = CommandTask("python -m pip install redengine", name="my_cmd_task_1")

    Or list of commands:

    >>> task = CommandTask(["python", "-m", "pip", "install", "redengine"], name="my_cmd_task_2")
    """
    timeout = None

    argforms = {
        "long": "--",
        "--": "--",
        "short": "-",
        "-": "-",
    }

    def __init__(self, command=None, shell=False, cwd=None, kwds_popen=None, argform="-", **kwargs):
        self.command = command
        self.argform = self.argforms[argform]
        super().__init__(**kwargs)
        self.kwargs_popen = {
            "cwd": cwd, 
            "shell":shell, 
            "stdin": subprocess.PIPE,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
        }
        if kwds_popen is not None:
            self.kwargs_popen.update(kwds_popen)
        # About shell: https://stackoverflow.com/a/36299483/13696660

    def execute(self, **parameters):
        """Run the command."""
        command = self.command
        
        for param, val in parameters.items():
            if not param.startswith("-"):
                param = self.argform + param

            if isinstance(command, str):
                command = command + f" {param} \"{val}\""
            else:
                command += [param] + [val]

        # https://stackoverflow.com/a/5469427/13696660
        pipe = subprocess.Popen(command, **self.kwargs_popen)
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

    def postfilter_params(self, params: Parameters):
        # Only allows the task specific parameters
        # for simplicity
        return params

    def get_default_name(self):
        command = self.action
        return command if isinstance(command, str) else ' '.join(command)

    @property
    def action(self):
        "Alias for command. Deprecated."
        warnings.warn(
            'CommandTask.action is deprecated ' 
            'and will be removed in the future release. '
            'Please use CommandTask.command instead', FutureWarning)
        return self.command