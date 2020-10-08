
import re

def has_module_in_repr(value):
    return bool(re.match("^[a-zA-Z0-9_]+[.].+", repr(value)))