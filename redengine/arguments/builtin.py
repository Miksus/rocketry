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
        >>> Arg.put_session(my_param_1=1, my_param_2=2)

        >>> from redengine import session
        >>> session.parameters
        Parameters(my_param_1=Arg(1), my_param_2=Arg(2))
    """
    def __init__(self, value:Any):
        self._value = value

    def get_value(self, task=None) -> Any:
        return self._value

    @classmethod
    def put_session(cls, **kwargs):
        for name, value in kwargs.items():
            cls.session.parameters[name] = cls(value)

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

    .. doctest:: funcarg

        >>> from redengine.arguments import FuncArg

    FuncArg can also set arguments directly to 
    ``session.parameters``. For example by decorating 
    a function:

    .. doctest:: funcarg

        >>> @FuncArg.put_session()
        ... def myarg1():
        ...     ...

    Note that the name of the argument in 
    ``session.parameters`` is the name of the 
    function ("myarg1"). The name can also
    be passed:

    .. doctest:: funcarg

        >>> @FuncArg.put_session("myarg2")
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
    def put_session(cls, name:str=None, *args, **kwargs):
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
                "Perhaps forgot to close .put_session()?"
            )
        return wrapper

    def __repr__(self):
        cls_name = type(self).__name__
        return f'{cls_name}({self.func.__name__})'