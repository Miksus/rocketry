
from atlas.core.conditions import Statement, Historical, Comparable
from atlas.core.parameters import GLOBAL_PARAMETERS


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
            found_val = GLOBAL_PARAMETERS[key]
        except KeyError:
            return False
        else:
            if val != found_val:
                return False
    return True
