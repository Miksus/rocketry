
import copy
from typing import Callable, Pattern, Union

from redengine.core.condition import BaseCondition #, Task
from redengine.core.parameters.arguments import BaseArgument

class _CondStatus(BaseArgument):

    @classmethod
    def to_session(cls, task_name, return_):
        if not isinstance(return_, bool):
            raise TypeError(f"Condition {task_name} state must be boolean. Given: {type(return_)}")
        if not hasattr(cls.session, "_cond_states"):
            cls.session._cond_states = {}
        cls.session._cond_states[task_name] = return_


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

        from redengine.conditions import TaskCond

        @TaskCond(syntax=re.compile("is foo at (?P<place>.+)"), start_cond="every 10 minutes")
        def is_foo(place):
            ... # Expensive check
            return True

    Using the condition:

    .. code-block:: python

        from redengine.tasks import FuncTask

        @FuncTask(start_cond="is foo at home")
        def mytask():
            ...

    """

    def __init__(self,
                 func: Callable[..., bool]=None,
                 active_time:str ="always",
                 syntax:Union[str, Pattern]=None, 
                 **kwargs):
        from redengine.parse import parse_time

        self.func = func
        self.syntax = syntax
        self.active_time = parse_time(active_time)

        self.kwds_task = kwargs

        if self.func is not None:
            self._set_parsing()

        if not hasattr(self.session, "_cond_states"):
            self.session._cond_states = {}

    def _set_task(self, *args, **kwargs) -> 'TaskCond':
        "Recreate the condition using args and kwargs"
        from redengine.tasks.func import FuncTask
        new_self = copy.copy(self)

        new_self.task = FuncTask(
            func=self.func,
            on_exists="rename",
            name=f"_condition-{self._get_func_name(self.func)}",
            parameters=kwargs,
            **self.kwds_task
        )
        new_self.task.return_arg = _CondStatus

        return new_self

    def __call__(self, func: Callable[..., bool]):
        self.func = func
        self._set_parsing()
        return func

    def __bool__(self):

        task_state = self.session._cond_states.get(self.task.name, False)
        if self.task.last_success is None or self.task.last_success not in self.active_time:
            # The cooldown period is gone --> setting to default
            self.state = False
        else:
            self.state = task_state
        return self.state

    def _set_parsing(self):
        from redengine.parse import CondParser
        self.session.cond_parsers[self.syntax] = CondParser(func=self._set_task, cached=True)

    def _get_func_name(self, func):
        func_module = func.__module__
        func_name = getattr(func, "__name__", type(func).__name__)
        if func_module == "__main__":
            # Showing as 'myfunc'
            return func_name
        else:
            # Showing as 'path.to.module:myfunc'
            return f"{func_module}:{func_name}"