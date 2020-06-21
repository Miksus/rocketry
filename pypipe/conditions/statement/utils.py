
from .base import Statement
from ..base import BaseCondition

import logging
logger = logging.getLogger(__name__)

from copy import copy

def _set_default_param(condition, **kwargs):
    if isinstance(condition, Statement):
        new_condition = condition.copy()
        for key, value in kwargs.items():
            if new_condition.has_param(key) and not new_condition.has_param_set(key):
                new_condition.kwargs[key] = value
    else:
        new_condition = condition
    return new_condition
        
def set_statement_defaults(condition, **kwargs):
    if isinstance(condition, BaseCondition):
        if hasattr(condition, "apply"):
            set_cond = condition.apply(_set_default_param, **kwargs)
        else:
            set_cond = _set_default_param(condition, **kwargs)
        return set_cond
    else:
        return condition