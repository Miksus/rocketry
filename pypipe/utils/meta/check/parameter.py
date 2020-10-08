
import inspect

"""
Utilities to check function/method parameters
"""

def has_default(param:inspect.Parameter):
    "Whether the parameter has default value"
    return param.default is not param.empty

def is_positional(param:inspect.Parameter):
    "Whether the parameter is positional argument"
    return param.kind is param.POSITIONAL_ONLY or param.kind is param.POSITIONAL_OR_KEYWORD

def is_keyword(param:inspect.Parameter):
    "Whether the parameter is keyword argument"
    return param.kind is param.KEYWORD_ONLY or param.kind is param.POSITIONAL_OR_KEYWORD

def is_args(param:inspect.Parameter):
    "Whether the parameter is wild card positional (like *args)"
    return param.kind is param.VAR_POSITIONAL

def is_kwargs(param:inspect.Parameter):
    "Whether the parameter is wild card keyword (like **kwargs)"
    return param.kind is param.VAR_KEYWORD