
from copy import copy, deepcopy
from functools import partial
from abc import abstractmethod
from inspect import signature
import datetime

import numpy as np

from atlas.core.parameters import Parameters

# TODO: convert Observation to a "statement" when comparison?
from .base import BaseCondition
#from .mixins import _Historical, Comparable

import logging
logger = logging.getLogger(__name__)


class Statement(BaseCondition):
    """

    @Statement
    def file_exists(filename):
        pass

    my_experiment(arg=5)

    Example:
        @Statement()
        def file_exists(name):
            ...
        
        file_exists(name="mydata.xlsx")

    historical example:
        @Statement(historical=True)
        def file_modified(start, end):
            ...
        
        file_modified.between("10:00", "11:00") # TimeInterval("10:00", "11:00")
        file_modified.between("Mon", "Fri")     # TimeOfWeek.between("Mon", "Fri")
        file_modified.between("1.", "15.")      # DaysOfMonth.between("1.", "15.")
        file_modified.past("2 hours")           # TimeDelta("2 hours")
        file_modified.in_("today")              # TimeInterval("00:00", "24:00")
        file_modified.in_("yesterday")          # TimeInterval("00:00", "24:00") - pd.Timedelta("1 day")
        file_modified.in_("hour")               # hourly

        file_modified.after(another_statement)  # file modified after last occurence of another_staement
        file_modified.before(another_statement) # file modified before first occurence of another_staement

    Quantitative example:
        @Statement(quantitative=True)
        def has_free_ram(relative=False):
            ...

        has_free_ram(relative=True).more_than(0.5)
        has_free_ram.more_than(900000)
        has_free_ram > 900000


    Quantitative & historical example:
        @Statement(historical=True, quantitative=True, pass_task=True)
        def has_run(task, start, end):
            ...
        
        has_run(mytask).between("10:00", "11:00").more_than(5) # TimeInterval("10:00", "11:00")
        has_run(mytask).between("Mon", "Fri").less_than(3)     # TimeOfWeek.between("Mon", "Fri")
        has_run(mytask).between("1.", "15.")                   # DaysOfMonth.between("1.", "15.")
        has_run(mytask).past("2 hours")                        # TimeDelta("2 hours")
        has_run(mytask).in_("today")                           # TimeInterval("00:00", "24:00")
        has_run(mytask).in_("yesterday")                       # TimeInterval("00:00", "24:00") - pd.Timedelta("1 day")
        has_run(mytask).in_("hour")                            # hourly
        has_run(mytask).in_cycle()                             # mytask.cycle

    Special
        Scheduler statement
            @Statement(quantitative=True, pass_scheduler=True)
            def tasks_alive(scheduler):
                ...

            tasks_alive == 0
    """

    name = None
    _use_global_params = False

    @classmethod
    def from_func(cls, func=None, *, historical=False, quantitative=False, use_globals=False):
        """Create statement from function (returns new class)
        
        Arguments:
        ----------
            func [callable] : Function to use as the "observe" method. Should return bool or 
                              an object that can be compared if quantitative=True
            historical [bool] : Whether the statement has a time window to check observation
            quantitative [bool] : Whether the statement can be compared (with <, >, ==, >=, etc.)
            use_globals [bool] : Whether to allow passing session.parameters to the observe method.
        """
        if func is None:
            # Acts as decorator
            return partial(cls.from_func, historical=historical, quantitative=quantitative, use_globals=use_globals)

        name = func.__name__
        #bases = (cls,)

        bases = []
        if historical: bases.append(Historical)
        if quantitative: bases.append(Comparable)
        bases.append(cls)
        bases = tuple(bases)

        attrs = {
            "_use_global_params": use_globals,
            # Methods
            "observe": staticmethod(func),
        }

        # Creating class dynamically
        cls = type(
            name,
            tuple(bases),
            attrs
        )
        return cls

    def __init__(self, *args, **kwargs):
        """Base for events

        Keyword Arguments:
            func {[type]} -- [description] (default: {None})
            quantitative {bool} -- Whether the statement function returns number
            historical {bool} -- Whether the statement has start and end times
        """

        self.args = args
        self.kwargs = kwargs

    def __bool__(self):
        try:
            outcome = self.observe(*self.args, **self.get_kwargs())
            status = self._to_bool(outcome)
        except (KeyboardInterrupt, ImportError) as exc:
            # Let these through
            raise
        except Exception as exc:
            logger.exception(f"Statement '{self}' is False due to an Exception.")
            # Exceptions are considered that the statement is false
            return False

        #logger.debug(f"Statement {str(self)} status: {status}")

        return status

    @abstractmethod
    def observe(self, *args, **kwargs):
        "Observe status of the statement (returns true/false)"
        return True

    def _to_bool(self, res):
        return bool(res)

    def get_kwargs(self):
        # TODO: Get session parameters
        if self._use_global_params:
            return self.session.parameters | self.kwargs
        else:
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

    def has_param(self, *params):
        sig = signature(self.observe)
        return all(param in sig.parameters for param in params)

    def has_param_set(self, *params):
        return all(param in self.kwargs for param in params)

    def __str__(self):
        name = self.name
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

class Comparable(Statement):
    # TODO
    pass

    def _to_bool(self, res):
        # For:
        # [1,2,3] --> 3
        # 
        if isinstance(res, bool):
            return super()._to_bool(res)

        res = len(res) if hasattr(res, "__len__") else res

        comps = {
            f"_{comp}_": self.kwargs[comp]
            for comp in ("_eq_", "_ne_", "_lt_", "_gt_", "_le_", "_ge_")
            if comp in self.kwargs
        }
        if not comps:
            return res > 0
        return all(
            getattr(res, comp)(val) # Comparison is magic method (==, !=, etc.)
            for comp, val in comps.items()
        )

# Quantitative extra
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

    def __init__(self, *args, period=None, **kwargs):
        self.period = period
        super().__init__(*args, **kwargs)

    def get_kwargs(self):
        kwargs = super().get_kwargs()
        if self.period is None:
            return kwargs

        dt = datetime.datetime.now()

        interval = self.period.rollback(dt)
        start = interval.left
        end = interval.right
        kwargs["_start_"] = start
        kwargs["_end_"] = end
        return kwargs

    def __eq__(self, other):
        # self == other
        is_same_class = isinstance(other, Historical)
        if is_same_class:
            # Not storing as parameter to statement but
            # check whether the statements are same
            has_same_period = self.period == other.period
            return super().__eq__(other) and has_same_period
        return super().__eq__(other)