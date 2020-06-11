
from copy import copy, deepcopy
from functools import partial
from abc import abstractmethod
from inspect import signature

import numpy as np

# TODO: convert Observation to a "statement" when comparison?
from ..base import BaseCondition


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
        file_modified.between("Mon", "Fri")     # DaysOfWeek.between("Mon", "Fri")
        file_modified.between("1.", "15.")      # DaysOfMonth.between("1.", "15.")
        file_modified.past("2 hours")           # TimeDelta("2 hours")
        file_modified.in_("today")              # TimeInterval("00:00", "24:00")
        file_modified.in_("yesterday")          # TimeInterval("00:00", "24:00") - pd.Timedelta("1 day")
        file_modified.in_("hour")               # hourly

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

    def __init__(self, experiment=None, *, quantitative=False, historical=False):
        """Base for events

        Keyword Arguments:
            experiment {[type]} -- [description] (default: {None})
            quantitative {bool} -- Whether the statement function returns number
            historical {bool} -- Whether the statement has start and end times
        """
        self._func = experiment
        self.quantitative = quantitative
        self.historical = historical

        if self.historical:
            self.period = None
        if self.quantitative:
            self.comparisons = {}

        self.args = ()
        self.kwargs = {}

    @property
    def function(self):
        return partial(
            self._func, 
            *self.args, 
            **self.kwargs
        )

    def __bool__(self):
        return self.observe()

    def observe(self, start=None, end=None):
        "Observe statement"
        kwargs = self.kwargs

        if self.historical:
            dt = self.current_datetime()
            interval = self.period.prev(dt)
            start = interval.left
            end = interval.right
            kwargs.update({"start": start, "end": end})

        outcome = self._func(*self.args, **kwargs)

        if self.quantitative:
            return all(
                getattr(outcome, comp)(val) 
                for comp, val in self.comparisons.items()
            )
        return outcome

    def past(self, *args, **kwargs):
        """
        Examples:
        ---------
            mystatement.past("1 days 5 hours")
        """
        period = TimeDelta(*args, **kwargs)
        if self.period is not None:
            self.period &= period
        else:
            self.period = period
    
    def between(self, start, end):
        # TODO: make from_slice to TimeInterval
        period = TimeInterval.from_slice(start, end)
        if self.period is not None:
            self.period &= period
        else:
            self.period = period

    def in_cycle(self):
        if not self.require_task:
            raise AttributeError("Statement does not require task")
        period = self.kwargs["task"].cycle

        if self.period is not None:
            self.period &= period
        else:
            self.period = period

    @property
    def require_task(self):
        return self.has_param("task")

    def __call__(self, *args, **kwargs):
        if not args and not kwargs:
            return self.experiment()

        if self._func is None:
            self._func = args[0]
            return self

        new = copy(self)

        if kwargs:
            new.kwargs = kwargs
        if args:
            new.args = args
        return new
        
    def set_params(self, *args, **kwargs):
        "Add arguments to the experiment"
        self.args = (*self.args, *args)
        self.kwargs.update(kwargs)


    def has_param(self, *params):
        sig = signature(self.experiment)
        return all(param in sig.parameters for param in params)

    def has_param_set(self, *params):
        return all(param in self.kwargs for param in params)

# Comparisons
    def __eq__(self, other):
        # self == other
        obs = copy(self)
        obs.comparisons["__ne__"] = other
        return obs

    def __ne__(self, other):
        # self != other
        obs = copy(self)
        obs.comparisons["__ne__"] = other
        return obs

    def __lt__(self, other):
        # self < other
        obs = copy(self)
        stmt.comparisons["__lt__"] = other
        return stmt

    def __gt__(self, other):
        # self > other
        obs = copy(self)
        obs.comparisons["__gt__"] = other
        return obs

    def __le__(self, other):
        # self <= other
        obs = copy(self)
        obs.comparisons["__le__"] = other
        return obs
        
    def __ge__(self, other):
        # self >= other
        obs = copy(self)
        obs.comparisons["__ge__"] = other
        return obs


