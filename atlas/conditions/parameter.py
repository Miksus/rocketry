
from atlas.core.conditions import Statement, Historical, Comparable, BaseCondition


class IsEnv(BaseCondition):
    """Condition checks whether session parameter 'env'
    has the given value. 
    """
    def __init__(self, env):
        self.env = env
    
    def __bool__(self):
        return self.session.parameters.get("env", None) == self.env

class IsParameter(BaseCondition):

    def __init__(self, **params):
        self.params = params
    
    def __bool__(self):
        return all(
            self.session.parameters[key] == val
            if key in self.session.parameters
            else False
            for key, val in self.params.items()
        ) 

@Statement.from_func(use_globals=False)
def ParamExists(**kwargs):
    """Whether session has given parameter and value
    
    Example:
    --------
        is_test = ParamExists(mode="test")
        session.parameters["mode"] = "test"
        assert is_test
    """
    for key, val in kwargs.items():
        try:
            found_val = Statement.session.parameters[key]
        except KeyError:
            return False
        else:
            if val != found_val:
                return False
    return True
