
import inspect
import importlib
from typing import Callable, Union

from redengine.core.task import Task
from redengine.core.utils import is_pickleable


class FuncTask(Task):
    """Task that executes a function or callable.

    Parameters
    ----------
    func : Callable, str
        Function or callable to be executed. If string is
        passed, the string should be in form "mypackage.mymodule:myfunc"
        and the mypackage should be in sys.path.
    **kwargs : dict
        See :py:class:`redengine.core.Task`


    Examples
    --------

    >>> from redengine.tasks import FuncTask
    >>> def myfunc():
    ...     ...
    >>> task = FuncTask(myfunc, name="my_func_task_1")

    **Via decorator:**

    >>> from redengine.tasks import FuncTask
    >>> @FuncTask(name='my_func_task_2', start_cond="daily")
    ... def myfunc():
    ...     ...

    If the ``name`` is not defined, the name will be in form
    ``path.to.module:myfunc``.

    Warnings
    --------

    If ``execution='process'``, only picklable functions can be used.
    The following will NOT work:

    .. code-block:: python

        # Lambda functions are not allowed
        FuncTask(lambda:None, execution="process")

    .. code-block:: python

        # nested functions are not allowed
        def my_func():
            @FuncTask(execution="process")
            def my_task_func():
                ...
        my_func()

    .. code-block:: python

        def my_decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper

        # decorated functions are not allowed
        @my_decorator
        @FuncTask(execution="process")
        def my_task_func():
            ...
    """
    func: Callable

    def __init__(self, func=None, **kwargs):
        if func is None:
            # FuncTask was probably called like:
            # @FuncTask(...)
            # def myfunc(...): ...

            # We initiate the class lazily by creating
            # almost empty shell class that is populated
            # in next __call__ (which should occur immediately)
            self._delayed_kwargs = kwargs
            return 
        elif not kwargs:
            # Most likely called as:
            # @FuncTask
            # def myfunc(...): ...
            
            # We are slightly forgiving and set 
            # the execution to else than process
            # as it's obvious it would not work.
            kwargs["execution"] = "thread"
        # Setting func requires 'execution'
        self.execution = kwargs.get("execution", self.default_execution)
        self.func = func
        super().__init__(**kwargs)

    def __call__(self, *args, **kwargs):
        if not hasattr(self, "_func"):
            func = args[0]
            self.execution = self._delayed_kwargs.get("execution", self.default_execution)
            self.func = func
            super().__init__(**self._delayed_kwargs)
            del self._delayed_kwargs

            # Note that we must return the function or 
            # we are in deep shit with multiprocessing
            # (or pickling the function).
            return func
        else:
            return super().__call__(*args, **kwargs)

    def execute(self, **kwargs):
        "Run the actual, given, task"
        return self.func(**kwargs)

    def get_default_name(self):
        return f"{self.func.__module__}:{self.func.__name__}"
        
    def prefilter_params(self, params):
        return {
            key: val for key, val in params.items()
            if key in self.kw_args
        }

    @staticmethod
    def get_reguired_params(func, params):
        sig = inspect.signature(func)
        required_params = [
            val
            for name, val in sig.parameters
            if val.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD, # Normal argument
                inspect.Parameter.KEYWORD_ONLY # Keyword argument
            )
        ]
        kwargs = {}
        for param in required_params:
            if param in params:
                kwargs[param] = params[param]
        return kwargs

    @property
    def pos_args(self):
        sig = inspect.signature(self.func)
        pos_args = [
            val.name
            for name, val in sig.parameters.items()
            if val.kind in (
                inspect.Parameter.POSITIONAL_ONLY, # NOTE: Python <= 3.8 do not have positional arguments, but maybe in the future?
                inspect.Parameter.POSITIONAL_OR_KEYWORD # Keyword argument
            )
        ]
        return pos_args

    @property
    def kw_args(self):
        sig = inspect.signature(self.func)
        kw_args = [
            val.name
            for name, val in sig.parameters.items()
            if val.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD, # Normal argument
                inspect.Parameter.KEYWORD_ONLY # Keyword argument
            )
        ]
        return kw_args

    @classmethod
    def decorate(cls, **kwargs):
        """FuncTask as a decorator"""
        def wrapper(func):
            return cls(func, **kwargs)
        return wrapper

    @property
    def func(self):
        return self._func

    @func.setter
    def func(self, func:Union[str, Callable]):
        if isinstance(func, str):
            if ":" in func:
                import_name, func_name = func.split(":")
            else:
                import_name, func_name = func.rsplit('.', 1)
            # Should be in form 'mypackage.mymodule:myfunc'
            module = importlib.import_module(import_name)
            func = getattr(module, func_name)

        if not callable(func):
            raise TypeError(f"FuncTask's function must be callable. Got: {type(func)}")
        elif self.execution == "process" and func.__name__ == "<lambda>":
            raise AttributeError(
                f"Cannot pickle lambda function '{func}'. "
                "The function must be pickleable if task's execution is 'process'. "
            )
        self._func = func
