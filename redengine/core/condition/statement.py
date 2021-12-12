
import logging
from copy import copy
from functools import partial
from abc import abstractmethod
import datetime
import time
from typing import Optional, Union

from redengine.core.time.base import TimePeriod
from .base import BaseCondition

logger = logging.getLogger(__name__)


class Statement(BaseCondition):
    """Base class for Statements.
    
    Statement is a base condition that
    require either inspecting historical
    events or doing a comparison of observed
    values to conclude whether the condition 
    holds.

    Parameters
    ----------
    *args : tuple
        Positional arguments for the ``observe``
        method.
    **kwargs : dict
        Keyword arguments for the ``observe``
        method.
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __bool__(self):
        outcome = self.observe(*self.args, **self.get_kwargs())
        status = self._to_bool(outcome)
        return status

    @abstractmethod
    def observe(self, *args, **kwargs):
        """Observe status of the statement (returns true/false).
        
        Override this to build own logic."""
        return True

    def _to_bool(self, res):
        return bool(res)

    def get_kwargs(self):
        # TODO: Get session parameters
        return self.kwargs

    def to_count(self, result):
        "Turn event result to quantitative number"
        if isinstance(result, (int, float)):
            return result
        else:
            return len(result)
        
    def set_params(self, *args, **kwargs):
        "Add arguments to the experiment"
        self.args = (*self.args, *args)
        self.kwargs.update(kwargs)

    def __str__(self):
        name = type(self).__name__
        return f"< Statement '{name}'>"

    def copy(self):
        # Cannot deep copy self as if task is in kwargs, failure occurs
        new = copy(self)
        new.kwargs = copy(new.kwargs)
        new.args = copy(new.args)
        return new

    def __eq__(self, other):
        "Equal operation"
        is_same_class = isinstance(other, type(self))
        if is_same_class:
            has_same_args = self.args == other.args
            has_same_kwargs = self.kwargs == other.kwargs
            return has_same_args and has_same_kwargs
        else:
            return False

    def __repr__(self):
        cls_name = type(self).__name__
        arg_str = ', '.join(map(repr, self.args))
        kwargs_str = ', '.join(f'{key}={repr(val)}' for key, val in self.kwargs.items())
        param_str = ""
        if arg_str:
            param_str = arg_str
        if kwargs_str:
            if param_str:
                param_str = param_str + ", "
            param_str = param_str + kwargs_str
        return f'{cls_name}({param_str})'


class Comparable(Statement):
    """Statement that can be compared.

    The ``.observe()`` method should 
    return either:

    - boolean: Whether the value is true or false
    - Iterable: inspected whether the length fulfills the given comparisons.
    - int, float: inspected whether the number fulfills the given comparisons. 

    Parameters
    ----------
    *args : tuple
        See ``Statement``.
    **kwargs : dict
        See ``Statement``.
    """
    _comp_attrs = ("_eq_", "_ne_", "_lt_", "_gt_", "_le_", "_ge_")
    def __init__(self, *args, **kwargs):
        kwargs = {
            key: int(val) if key in self._comp_attrs else val
            for key, val in kwargs.items()
        }
        super().__init__(*args, **kwargs)

    def _to_bool(self, res):
        if isinstance(res, bool):
            return super()._to_bool(res)

        res = len(res) if hasattr(res, "__len__") else res

        comps = {
            f"_{comp}_": self.kwargs[comp]
            for comp in self._comp_attrs
            if comp in self.kwargs
        }
        if not comps:
            return res > 0
        return all(
            getattr(res, comp)(val) # Comparison is magic method (==, !=, etc.)
            for comp, val in comps.items()
        )

    def any_over_zero(self):
        # Useful for optimization: just find any observation and the statement is true
        comps = {
            comp: self.kwargs[comp]
            for comp in self._comp_attrs
            if comp in self.kwargs
        }
        if comps == {"_gt_": 0} or comps == {"_ge_": 1} or comps == {"_gt_": 0, "_ge_": 1}:
            return True
        return not comps

    def equal_zero(self):
        comps = {
            comp: self.kwargs[comp]
            for comp in self._comp_attrs
            if comp in self.kwargs
        }
        return comps == {"_eq_": 0}

    def __eq__(self, other):
        # self == other
        is_same_class = isinstance(other, Comparable)
        if is_same_class:
            # Not storing as parameter to statement but
            # check whether the statements are same
            return super().__eq__(other)
        return self._set_comparison("_eq_", other)

    def __ne__(self, other):
        # self != other
        return self._set_comparison("_ne_", other)

    def __lt__(self, other):
        # self < other
        return self._set_comparison("_lt_", other)

    def __gt__(self, other):
        # self > other
        return self._set_comparison("_gt_", other)

    def __le__(self, other):
        # self <= other
        return self._set_comparison("_le_", other)
        
    def __ge__(self, other):
        # self >= other
        return self._set_comparison("_ge_", other)        

    def _set_comparison(self, key, val):
        obj = self.copy()
        obj.kwargs[key] = val
        return obj

    def get_kwargs(self):
        return super().get_kwargs()


class Historical(Statement):
    """Statement that has history.

    The ``.observe()`` method is supplemented with 
    (if period passed to init):

    - ``_start_``: Start time of the statement period
    - ``_end_``: End time of the statement period

    Parameters
    ----------
    *args : tuple
        See ``Statement``.
    period : TimePeriod
        Time period the statement should hold.
    **kwargs : dict
        See ``Statement``.
    """

    def __init__(self, *args, period:Optional[Union[TimePeriod, str]]=None, **kwargs):
        from redengine.parse.time import parse_time
        self.period = parse_time(period) if isinstance(period, str) else period
        super().__init__(*args, **kwargs)

    def get_kwargs(self):
        kwargs = super().get_kwargs()
        if self.period is None:
            return kwargs

        dt = datetime.datetime.fromtimestamp(time.time())

        interval = self.period.rollback(dt)
        start = interval.left
        end = interval.right
        kwargs["_start_"] = start
        kwargs["_end_"] = end
        return kwargs

    def __eq__(self, other):
        # self == other
        is_same_class = isinstance(other, type(self))
        if is_same_class:
            # Not storing as parameter to statement but
            # check whether the statements are same
            has_same_period = self.period == other.period
            return super().__eq__(other) and has_same_period
        return super().__eq__(other)

    def __repr__(self):
        string = super().__repr__()
        period = self.period
        if period is not None:
            base_string = string[:-1]
            if base_string[-1] != "(":
                base_string = base_string + ", "
            return base_string + f"period={repr(self.period)})"
        else:
            return string