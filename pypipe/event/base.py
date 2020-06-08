
from copy import copy, deepcopy
from functools import partial
from abc import abstractmethod
from inspect import signature

import numpy as np

# TODO: convert Observation to a "statement" when comparison?


class Observation:
    """

    @Event
    def my_experiment(arg):
        pass

    my_experiment(arg=5)
    """

    def __init__(self, experiment=None, *, quantitative=False, historical=False):
        """Base for events

        Keyword Arguments:
            experiment {[type]} -- [description] (default: {None})
            quantitative {bool} -- Whether the experiment returns number
            historical {bool} -- Whether the experiment has start and end times
        """
        self._func = experiment
        self.quantitative = quantitative
        self.historical = historical

        self.comparisons = {}
        self.args = ()
        self.kwargs = {}

    @property
    def experiment(self):
        return partial(
            self._func,
            *self.args, **self.kwargs
        )

    @property
    def require_task(self):
        return self.has_param("task")

    def __bool__(self):
        "So that the event can be called like a condition though not being one"
        return self.observe()

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

    def observe(self, start=None, end=None):
        
        kwargs = self.kwargs
        if start is not None and end is not None:
            kwargs.update({"start": start, "end": end})
        outcome = self._func(*self.args, **kwargs)
        if self.quantitative:
            return all(
                getattr(outcome, comp)(val) 
                for comp, val in self.comparisons.items()
            )
        return outcome

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


