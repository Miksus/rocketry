
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
        
def set_statement_defaults2(condition, **kwargs):
    if isinstance(condition, BaseCondition):
        if hasattr(condition, "apply"):
            set_cond = condition.apply(_set_default_param, **kwargs)
        else:
            set_cond = _set_default_param(condition, **kwargs)
        return set_cond
    else:
        return condition


from collections.abc import Iterable
from copy import deepcopy

def _has_sub_conditions(obj):
    return isinstance(obj, Iterable)

def _set_statement_default(cond, **kwargs):
    if isinstance(cond, Statement):
        for key, default in kwargs.items():
            default_not_set = key not in cond._kwargs
            if default_not_set:
                cond._kwargs[key] = default

def _set_default(cond, **kwargs):
    if not _has_sub_conditions(cond):
        _set_statement_default(cond, **kwargs)
        return

    for sub_cond in cond:
        if _has_sub_conditions(sub_cond):
            _set_default(sub_cond, **kwargs)
        else:
            _set_statement_default(sub_cond, **kwargs)
    
def set_statement_defaults(cond, **kwargs):
    #cond = deepcopy(cond)
    _set_default(cond, **kwargs)
    #return cond