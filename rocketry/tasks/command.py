
import subprocess
from typing import List, Optional, Union

try:
    from typing import Literal
except ImportError: # pragma: no cover
    from typing_extensions import Literal

from pydantic import Field, validator

from rocketry.core.parameters.parameters import Parameters
from rocketry.core.task import Task


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
        See :py:class:`rocketry.core.Task`

    Examples
    --------

    >>> from rocketry.tasks import CommandTask
    >>> task = CommandTask("python -m pip install rocketry", name="my_cmd_task_1")

    Or list of commands:

    >>> task = CommandTask(["python", "-m", "pip", "install", "rocketry"], name="my_cmd_task_2")
    """

    command: Union[str, List[str]]
    shell: bool = False
    cwd: Optional[str]
    kwds_popen: dict = {}
    argform: Optional[Literal['-', '--', 'short', 'long']] = Field(description="Whether the arguments are turned as short or long form command line arguments")

    def get_kwargs_popen(self) -> dict:
        kwargs = {
            "cwd": self.cwd,
            "shell": self.shell,
            "stdin": subprocess.PIPE,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
        }
        kwargs.update(self.kwds_popen)
        return kwargs

    @validator('argform')
    def parse_argform(cls, value):
        return {
            "long": "--",
            "--": "--",
            "short": "-",
            "-": "-",
            None: '--',
        }[value]

    def execute(self, **parameters):
        """Run the command."""
        command = self.command

        for param, val in parameters.items():
            if not param.startswith("-"):
                param = self.argform + param

            if isinstance(command, str):
                command += f" {param} \"{val}\""
            else:
                command += [param] + [val]

        # https://stackoverflow.com/a/5469427/13696660
        pipe = subprocess.Popen(command, **self.get_kwargs_popen())
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

    def get_default_name(self, command, **kwargs):
        return command if isinstance(command, str) else ' '.join(command)
