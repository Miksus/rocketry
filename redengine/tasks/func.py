


from typing import Callable
from redengine.core.task import Task
#from .config import parse_config

from pathlib import Path
import inspect
import importlib
import subprocess
import re


class FuncTask(Task):
    """Task that executes a function or callable.

    Parameters
    ----------
    func : Callable
        Function or callable to be executed.
    **kwargs : dict
        See :py:class:`redengine.core.Task`

    """
    func: Callable

    def __init__(self, func, **kwargs):
        self.func = func
        super().__init__(**kwargs)

    def execute_action(self, **kwargs):
        "Run the actual, given, task"
        return self.func(**kwargs)

    def get_default_name(self):
        return self.func.__name__
        
    def filter_params(self, params):
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
