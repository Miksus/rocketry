
from typing import Any, Callable

from redengine.core.parameters import BaseArgument
from redengine.core.utils import filter_keyword_args

class Arg(BaseArgument):
    """A simple argument.

    Parameters
    ----------
    value : Any
        Value of the argument.

    Examples
    --------

    .. doctest:: arg

        >>> from redengine.arguments import Arg
        >>> Arg.to_session(my_param_1=1, my_param_2=2)

        >>> from redengine import session
        >>> session.parameters
        Parameters(my_param_1=Arg(1), my_param_2=Arg(2))
    """
    def __init__(self, value:Any):
        self._value = value

    def get_value(self, task=None) -> Any:
        return self._value

    @classmethod
    def to_session(cls, **kwargs):
        for name, value in kwargs.items():
            cls.session.parameters[name] = cls(value)

class Return(BaseArgument):
    """A return argument

    Return is an argument which value represents
    the return of a task.

    Parameters
    ----------
    name : str
        Name of the task which return value the argument 
        represents.

    Examples
    --------

    .. code-block:: python

        from redengine.arguments import Return
        from redengine.tasks import FuncTask

        # Create a task with a return
        @FuncTask()
        def my_task_1():
            ...
            return data

        @FuncTask(parameters={"myarg": Return('my_task_1')})
        def my_task_2(myarg):
            ...
    """

    def __init__(self, task_name, default=None):
        self.task_name = task_name
        self.default = default

    def get_value(self, task=None) -> Any:
        if self.task_name not in self.session.tasks:
            raise KeyError(f"Task {repr(self.task_name)} does not exists. Cannot get return value")
        return self.session.returns.get(self.task_name, self.default)

    def stage(self, task=None):
        return Arg(self.get_value())

    @classmethod
    def to_session(cls, task_name, return_):
        "Set the return to return parameters"
        if return_ is not None:
            cls.session.returns[task_name] = return_

class FuncArg(BaseArgument):
    """An argument which value is defined by the 
    return value of given function.

    Parameters
    ----------
    func : Callable
        Function that is executed and passed as value.
    *args : tuple
        Positional arguments passed to func.
    **kwargs : dict
        Keyword arguments passed to func.

    Examples
    --------

    Simple example:

    .. code-block:: python

        from redengine.tasks import FuncTask
        from redengine.arguments import FuncArg

        def my_func():
            ...
            return obj

        @FuncTask(parameters={"my_param": FuncArg(my_func)})
        def my_task(my_param):
            ...

    Example to set to session:

    .. doctest:: funcarg

        >>> from redengine.arguments import FuncArg

    FuncArg can also set arguments directly to 
    ``session.parameters``. For example by decorating 
    a function:

    .. doctest:: funcarg

        >>> @FuncArg.to_session()
        ... def myarg1():
        ...     ...

    Note that the name of the argument in 
    ``session.parameters`` is the name of the 
    function ("myarg1"). The name can also
    be passed:

    .. doctest:: funcarg

        >>> @FuncArg.to_session("myarg2")
        ... def myfunc(session):
        ...     ... # FuncArgs can also operate on session

    The ``session.parameters`` were updated.

    .. doctest:: funcarg

        >>> from redengine import session
        >>> session.parameters
        Parameters(myarg1=FuncArg(myarg1), myarg2=FuncArg(myfunc))
    """
    def __init__(self, func:Callable, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = self._get_kwargs(kwargs)

    def _get_kwargs(self, kwargs):
        defaults = {
            "session": self.session,
        }
        defaults.update(kwargs)
        return filter_keyword_args(self.func, defaults)

    def get_value(self, task=None):
        return self(task=task)

    def __call__(self, **kwargs):
        kwargs.update(self.kwargs)
        kwargs = filter_keyword_args(self.func, kwargs)
        return self.func(*self.args, **kwargs)

    @classmethod
    def to_session(cls, name:str=None, *args, **kwargs):
        """Create FuncArg from decorator
        and put the argument to the session
        parameters."""
        def wrapper(func):
            nonlocal name
            if name is None:
                name = func.__name__
            cls.session.parameters[name] = cls(func, *args, **kwargs)

            # NOTE: we need to return the function to prevent
            # issues in pickling (does not like we return
            # any other type).
            return func

        if callable(name):
            raise TypeError(
                "Argument name should be a string or None. " 
                f"Given: {type(name)}. "
                "Perhaps forgot to close .to_session()?"
            )
        return wrapper

    def __repr__(self):
        cls_name = type(self).__name__
        return f'{cls_name}({self.func.__name__})'