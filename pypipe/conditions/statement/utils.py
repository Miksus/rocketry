
from .base import Statement
from ..base import BaseCondition

def _set_default_param(condition, **kwargs):
    if isinstance(condition, Statement):
        for key, value in kwargs.items():
            if condition.has_param(key) and not condition.has_param_set(key):
                condition.kwargs[key] = value
        
def set_statement_defaults(condition, **kwargs):
    if isinstance(condition, BaseCondition):
        if hasattr(condition, "apply"):
            condition.apply(_set_default_param, **kwargs)
        else:
            _set_default_param(condition, **kwargs)