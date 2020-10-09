
from copy import copy, deepcopy
from functools import partial
from abc import abstractmethod
from inspect import signature

import numpy as np

# TODO: convert Observation to a "statement" when comparison?
from ..base import BaseCondition
from .mixins import _Historical, _Quantitative

import logging
logger = logging.getLogger(__name__)

class Statement(BaseCondition, _Historical, _Quantitative):
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
        file_modified.between("Mon", "Fri")     # DaysOfWeek.between("Mon", "Fri")
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
        has_run(mytask).between("Mon", "Fri").less_than(3)     # DaysOfWeek.between("Mon", "Fri")
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

    def __init__(self, func=None, *, quantitative=False, historical=False):
        """Base for events

        Keyword Arguments:
            func {[type]} -- [description] (default: {None})
            quantitative {bool} -- Whether the statement function returns number
            historical {bool} -- Whether the statement has start and end times
        """
        self._func = func
        self.quantitative = quantitative
        self.historical = historical

        if self.historical:
            self._init_historical()

        if self.quantitative:
            self._init_quantitative()

        self.args = ()
        self._kwargs = {}

    @property
    def function(self):
        return partial(
            self._func, 
            *self.args, 
            **self.kwargs
        )

    def __bool__(self):
        try:
            outcome = self._func(*self.args, **self.kwargs)
        except IndexError:
            # Exceptions are considered that the statement is false
            return False
        result = self.to_boolean(outcome)

        logger.debug(f"Statement {str(self)} status: {result}")

        return result

    @property
    def kwargs(self):
        kwargs = self._kwargs
        if self.historical:
            kwargs.update(self.get_time_kwargs())
        return kwargs

    def to_boolean(self, result):
        
        if self.historical and not self.has_param("_start_", "_end_"):
            # result should be datelike or list of datelike
            # TODO: This is NOT working
            start = self.get_start()
            end = self.get_end()
            if is_datelike(result):
                result = start < result < end
            else:
                # List of datelike
                result = [
                    event
                    for event in result
                    if start < event < end
                ]

        if self.quantitative:
            result = self.to_count(result)
            comparisons = self.comparisons or {"__gt__": 0}
            return all(
                getattr(result, comp)(val) # Comparison is magic method (==, !=, etc.)
                if comp.startswith("__") and comp.endswith("__")
                else val(result) # val is function (like: "every": lambda...)
                for comp, val in comparisons.items()
            )
        else:
            return bool(result)

    def to_count(self, result):
        "Turn event result to quantitative number"
        if isinstance(result, (int, float)):
            return result
        else:
            return len(result)

    def next_trigger(self):
        "Get next datetime when the event can be the opposing value"
        # TODO: find better name
        # TODO: Is there better way?
        if not self.historical:
            raise AttributeError("Statement is not historical")
        occurrences = self()
        is_occurring = bool(self)
        if is_occurring:
            continue_to_occur = all(limiting not in self.comparisons for limiting in ("__eq__", "__ne__", "__le__", "__lt__"))
            if is_occurring and continue_to_occur:
                if isinstance(self.period, TimeInterval):
                    return self.period.rollforward(self.current_datetime).left
                elif isinstance(self.period, TimeCycle):
                    return self.period.rollforward(self.current_datetime).left
                elif isinstance(self.period, TimeDelta):
                    oldest_occurrence = min(sorted(occurrences)[-more_or_equal:])
                    return self.period.rollforward(oldest_occurrence).right

    @property
    def cycle(self):
        if self.historical:
            return self.period
            
    @property
    def require_task(self):
        return self.has_param("task")

    def __call__(self, *args, **kwargs):
        if not args and not kwargs:
            return self.function()

        if self._func is None:
            # Completing statement
            self._func = args[0]
            return self

        new = self.copy()

        new.set_params(*args, **kwargs)
        return new
        
    def set_params(self, *args, **kwargs):
        "Add arguments to the experiment"
        self.args = (*self.args, *args)
        self._kwargs.update(kwargs)

    def has_param(self, *params):
        sig = signature(self._func)
        return all(param in sig.parameters for param in params)

    def has_param_set(self, *params):
        return all(param in self.kwargs for param in params)

    def __str__(self):
        name = self._func.__name__
        return f"< Statement '{name}'>"

    @property
    def name(self):
        return self._func.__name__

    def copy(self):
        # Cannot deep copy self as if task is in kwargs, failure occurs
        new = copy(self)
        if hasattr(self, "comparisons"):
            new.comparisons = copy(self.comparisons)
        if hasattr(self, "period"):
            new.period = copy(self.period)
        new._kwargs = copy(new._kwargs)
        new.args = copy(new.args)
        return new