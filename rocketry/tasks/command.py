
import asyncio
import time
import subprocess
from typing import List, Optional, Union

from pyparsing import warnings

try:
    from typing import Literal
except ImportError: # pragma: no cover
    from typing_extensions import Literal

from pydantic import Field, validator

from rocketry.core.parameters.parameters import Parameters
from rocketry.core.task import Task
from rocketry.args import TerminationFlag
from rocketry.exc import TaskTerminationException

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
    text: bool = True
    cwd: Optional[str]
    kwds_popen: dict = {}
    argform: Optional[Literal['-', '--', 'short', 'long']] = Field(description="Whether the arguments are turned as short or long form command line arguments", default="--")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.get_execution() == "process":
            warnings.warn(f"CommandTask {self.name} will create redundant process. Consider setting execution as 'async' or 'thread'")

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
        }[value]

    async def execute(self, **parameters):
        """Run the command."""
        execution = self.execution
        command = self.command
        flag_terminate = parameters.pop("__flag_terminate", None)

        for param, val in parameters.items():
            if not param.startswith("-"):
                param = self.argform + param

            if isinstance(command, str):
                command += f" {param} \"{val}\""
            else:
                command += [param] + [val]

        kwds = self.get_kwargs_popen()
        process = await asyncio.create_subprocess_exec(*command, **kwds)
        if execution == "thread":
            while process.returncode is None:
                if flag_terminate.is_set():
                    process.kill()
                    raise TaskTerminationException()
                time.sleep(0.1)
        else:
            await process.wait()

        return_code = process.returncode
        if return_code != 0:
            errs = await process.stderr.read()
            if hasattr(errs, "decode"):
                errs = errs.decode("utf-8", errors="ignore")
            raise OSError(f"Failed running command ({return_code}): \n{errs}")
        out = await process.stdout.read()
        if self.text:
            out = self._to_text(out)
        return out

    def get_task_params(self):
        task_params = super().get_task_params()
        task_params.update({'__flag_terminate': TerminationFlag()})
        return task_params

    def _to_text(self, s:Union[bytes, str]) -> str:
        if hasattr(s, "decode"):
            s = s.decode("utf-8", errors="ignore")
        return s

    def postfilter_params(self, params: Parameters):
        # Only allows the task specific parameters
        # for simplicity
        return params

    def get_default_name(self, command, **kwargs):
        return command if isinstance(command, str) else ' '.join(command)
