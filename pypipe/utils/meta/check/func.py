
import inspect
from .parameter import is_args, is_kwargs

"""
Utilities to check whether a function has specific properties
"""

def has_args(func):
    s = inspect.signature(func)
    return any(is_args(param) for param in s.parameters.values())

def has_kwargs(func):
    s = inspect.signature(func)
    return any(is_kwargs(param) for param in s.parameters.values())