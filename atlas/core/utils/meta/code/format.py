

"""
Functions to turn various objects to code
"""

from typing import Tuple

from ..check.strong_type import is_builtin, is_class, is_function, is_instance, is_module
from ..getters import get_classname, get_modulename
from .repr import has_module_in_repr

def declare_variable(var, value=None, expression:str=None, **kwargs) -> Tuple[str, str]:
    """Turn value or expression to variable declaration

    Args:
        var ([type]): Variable name
        value ([type], optional): Value to turn to variable declaration. Defaults to None.
        expression ([type], optional): Expression as string that is used as is. Defaults to None.

    Returns:
        [str]: Declaration line
        [str]: Importing line
    """
    if expression is None:
        expression, imports = to_expression(value)
    elif expression is None and value is None:
        expression, imports = "None", ""
    line = f"{var} = {expression}"
    return line, imports

def to_expression(value):
    """Turn value to expression string that can create the value with eval

    Returns: 
        [str]: Expression line
        [str]: Importing lines
    """
    #if self.is_container(value):
    #    pass
    if is_instance(value):
        expr = repr(value)
    elif is_class(value):
        expr = value.__qualname__
    elif callable(value):
        expr = value.__qualname__
    elif is_module(value):
        expr = value.__spec__.name
        # See that expr will be like: pandas.tseries
        # and impr will be like: import pandas.tseries
    
    impr = get_import(value)
    return expr, impr

def get_import(value) -> str:
    "Make an import statement that imports value's class/variable/module/function"
    if is_builtin(value) or get_modulename(value) == "__main__":
        # No need to import anything
        return None
    elif is_module(value):
        return f"import {value.__name__}"
    elif has_module_in_repr(value):
        # Like datetime.datetime, no need to import the object but just the base of the library
        return f"import {get_modulename(value)}"
    else:
        # If value is an instance, we cannot know whether the instance has been inititated
        # in main or in the package/module. We assume it's initiated in the main
        return f"from {get_modulename(value)} import {get_classname(value) if is_instance(value) else value.__name__}"