
from typing import Mapping
from powerbase.core.conditions import Statement, Historical, Comparable, BaseCondition


class IsEnv(BaseCondition):
    """Condition checks whether session parameter 'env'
    has the given value. 
    """
    __parsers__ = {re.compile(r"env '(?P<env>.+)'"): "__init__"}

    def __init__(self, env):
        self.env = env
    
    def __bool__(self):
        return self.session.parameters.get("env", None) == self.env

class ParamExists(BaseCondition):
    """Condition to check whether a parameter (and its value)
    exists.

    Examples
    --------
    >>> session.parameters = {"x": 1, "y": 2, "z": 3}

    >>> ParamExists(x=1, y=2)
    True
    >>> ParamExists(x=1, z=-999)
    False
    >>> ParamExists("x", "y", "z")
    True
    >>> ParamExists("x", "y", "k")
    False
    """
    param_keys:dict
    param_vals:tuple

    def __init__(self, *param_keys, **param_vals):
        self.param_keys = param_keys
        self.param_values = param_vals
    
    def __bool__(self):
        params = self.session.parameters
        for key in self.param_keys:
            if key not in params:
                return False
        for key, val in self.param_values.items():
            if key not in params:
                return False
            elif params[key] != val:
                return False
        # Passed all test
        return True
