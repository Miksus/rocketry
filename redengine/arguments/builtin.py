from typing import Any, Callable
from redengine.core.parameters import BaseArgument

class Argument(BaseArgument):
    """A simple argument.

    Parameters
    ----------
    value : Any
        Value of the argument
    """
    def __init__(self, value:Any):
        self._value = value

    def get_value(self, task=None) -> Any:
        return self._value


class FuncArg(BaseArgument):
    """Argument which value is the return value
    of a function.

    Parameters
    ----------
    func : Callable
        Function that is executed and passed as value.
    *args : tuple
        Positional arguments passed to func.
    **kwargs : dict
        Keyword arguments passed to func.
    """
    def __init__(self, func:Callable, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def get_value(self, task=None):
        return self()

    def __call__(self):
        return self.func(*self.args, **self.kwargs)