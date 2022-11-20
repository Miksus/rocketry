
import copy
from typing import Callable, Optional, Pattern, Union

from pydantic import Field
from rocketry.args import Session
from rocketry import Session as _Session

from rocketry.core.condition import BaseCondition #, Task
from rocketry.tasks.func import FuncTask


class _FuncTaskCondWrapper(FuncTask):

    # For some reason, the order of cls attrs broke here so we need to reorder then:
    session: _Session
    name: Optional[str] = Field(description="Name of the task. Must be unique")

    def _handle_return(self, value):
        # Handle the return value of the function
        self.session._cond_states[self.name] = value

class TaskCond(BaseCondition):
    """Condition which state is defined by a task

    TaskCond is a similar condition as ``FuncCond``
    except the a task is formed from the function. This
    condition is useful for checks that may be slow
    in terms of IO or by other system resources or could
    get stuck.

    The produced task will run depending on its ``start_cond``
    and the last check is considered to be valid given
    the ``active_time``. For example, you can set the
    task to run every 10 minutes to reduce the amount of
    time the condition needs to be checked.

    .. note::

        Multiple tasks may be created when using a TaskCond
        with different paramters.

    Parameters
    ----------
    func : Callable, optional
        Function to check for the condition state.
        Can also be passed as via decorator.
    active_time : str
        Time how long the previous time check is valid
        until the condition is considered ``False``,
        defaults 'never'
    syntax : str, re.compile
        Syntax for the condition to be used in
        condition creation (ie. Task's start_cond)
    **kwargs : dict
        Passed to ``FuncTask`` as arguments.

    Examples
    --------
    .. code-block:: python

        from rocketry.conditions import TaskCond

        @TaskCond(syntax=re.compile("is foo at (?P<place>.+)"), start_cond="every 10 minutes")
        def is_foo(place):
            ... # Expensive check
            return True

    Using the condition:

    .. code-block:: python

        from rocketry.tasks import FuncTask

        @FuncTask(start_cond="is foo at home")
        def mytask():
            ...

    """

    def __init__(self,
                 session,
                 func: Callable[..., bool]=None,
                 active_time:str ="always",
                 syntax:Union[str, Pattern]=None,
                 **kwargs):
        from rocketry.parse import parse_time

        self.func = func
        self.syntax = syntax
        self.active_time = parse_time(active_time, session=session)

        self.kwds_task = kwargs

        if self.func is not None:
            self._set_parsing()

        self.session = session

    def _set_task(self, *args, **kwargs) -> 'TaskCond':
        "Recreate the condition using args and kwargs"
        new_self = copy.copy(self)

        new_self.task = _FuncTaskCondWrapper(
            func=self.func,
            #on_exists="rename",
            name=f"_condition-{self._get_func_name(self.func)}",
            parameters=kwargs,
            session=self.session,
            **self.kwds_task
        )

        return new_self

    def __call__(self, func: Callable[..., bool]):
        self.func = func
        self._set_parsing()
        return func

    def get_state(self, session=Session()):
        last_success = self.task.last_success
        task_state = session._cond_states.get(self.task.name, False)
        active_time = self.active_time
        if hasattr(active_time, "use_reference"):
            active_time = active_time.use_reference(session._get_datetime_now())
        if last_success is not None and last_success not in active_time:
            # The cooldown period is gone --> setting to default
            self.state = False
        else:
            self.state = task_state
        return self.state

    def _set_parsing(self):
        from rocketry.parse import CondParser
        self.session._cond_parsers[self.syntax] = CondParser(func=self._set_task, session=self.session, cached=True)

    def _get_func_name(self, func):
        func_module = func.__module__
        func_name = getattr(func, "__name__", type(func).__name__)
        if func_module == "__main__":
            # Showing as 'myfunc'
            return func_name
        # Showing as 'path.to.module:myfunc'
        return f"{func_module}:{func_name}"
