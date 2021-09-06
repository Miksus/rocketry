
import inspect
import io
import os
import types

from .. import getters

"""
Utility checks containing type checking (or kind of type checking)
"""

def is_instance(value):
    "Check whether the value is an object of a class"
    return not is_class(value) and not is_function(value) and not is_module(value)

def is_function(value):
    "Check whether the value is a function"
    return isinstance(value, (types.BuiltinFunctionType, types.FunctionType))

def is_generator(value):
    return isinstance(value, types.GeneratorType)

def is_method(value):
    return isinstance(value, types.MethodType)

def is_class(value):
    "Check whether the value is a class"
    return inspect.isclass(value)

def is_module(value):
    "Check whether the value is a module"
    return type(value).__name__ == "module"

def is_builtin(value):
    "Check whether the value is a function"
    return getters.get_modulename(value) == "builtins"

def is_filelike(value):
    "Check if the value is file-like (note: pathlib.Path tests negative)"
    return (
        isinstance(value, io.TextIOBase)
        or isinstance(value, io.BufferedIOBase)
        or isinstance(value, io.RawIOBase)
        or isinstance(value, io.IOBase)
    )

def is_pathlike(value):
    "Check if the value is path-like"
    return isinstance(value, os.PathLike)