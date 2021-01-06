
from .check import strong_type

def get_modulename(value):
    if strong_type.is_module(value):
        return value.__name__
    elif strong_type.is_class(value) or strong_type.is_function(value):
        return value.__module__
    else:
        return type(value).__module__

def get_classname(value):
    return type(value).__name__