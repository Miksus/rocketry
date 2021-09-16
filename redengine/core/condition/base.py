import re
import datetime
from abc import abstractmethod
from typing import Callable, Dict, Pattern, Union, Type

from redengine.core.meta import _add_parser, _register


CLS_CONDITIONS: Dict[str, Type['BaseCondition']] = {}
PARSERS: Dict[Union[str, Pattern], Union[Callable, 'BaseCondition']] = {}


class _ConditionMeta(type):
    def __new__(mcs, name, bases, class_dict):

        cls = type.__new__(mcs, name, bases, class_dict)

        # Store the name and class for configurations
        # so they can be used in dict construction
        _register(cls, CLS_CONDITIONS)

        # Add the parsers
        _add_parser(cls, container=PARSERS)
        return cls


class BaseCondition(metaclass=_ConditionMeta):
    """Condition is a thing/occurence that should happen in order to something happen

    In scheduler's point of view the occurence/thing could be:
        - A job must be run
        - Current time of day should be afternoon
        - Must have enough RAM
    And the thing to happen when the condition is true could be:
        - Task is run
        - Task is killed
        - Scheduler is killed
        - Scheduler is maintained

    Examples
    --------

    Minimum example:

    >>> from redengine.core import BaseCondition
    >>> class MyCondition(BaseCondition):
    ...     def __bool__(self):
    ...         ... # Code that defines state either 
    ...         return True

    Complicated example with parser:

    >>> import os, re
    >>> class IsFooBar(BaseCondition):
    ...     __parsers__ = {
    ...         re.compile(r"is foo '(?P<outcome>.+)'"): "__init__"
    ...     }
    ...
    ...     def __init__(self, outcome):
    ...         self.outcome = outcome
    ...
    ...     def __bool__(self):
    ...         return self.outcome == "bar"
    ...
    ...     def __repr__(self):
    ...         return f"IsFooBar('{self.outcome}')"
    ...
    >>> from redengine.parse import parse_condition
    >>> parse_condition("is foo 'bar'")
    IsFooBar('bar')

    """
    # The session (set in redengine.session)
    session = None

    __parsers__ = {}
    __register__ = False

    @abstractmethod
    def __bool__(self):
        pass

    def __and__(self, other):
        # self & other
        # bitwise and
        # using & operator

        return All(self, other)

    def __or__(self, other):
        # self | other
        # bitwise or

        return Any(self, other)

    def __invert__(self):
        # ~self
        # bitwise not
        return Not(self)

    def __eq__(self, other):
        "Equal operation"
        is_same_class = isinstance(other, type(self))
        return is_same_class

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        else:
            raise AttributeError


class _ConditionContainer:
    "Wraps another condition"

    def flatten(self):
        conditions = []
        for attr in self._cond_attrs:
            conds = getattr(self, attr)

            conditions += conds
        return conditions
        
    def __getitem__(self, val):
        return self.subconditions[val]

    def __iter__(self):
        return iter(self.subconditions)

    def __eq__(self, other):
        "Equal operation"
        is_same_class = isinstance(other, type(self))
        if is_same_class:
            return self.subconditions == other.subconditions
        else:
            return False


class Any(_ConditionContainer, BaseCondition):

    def __init__(self, *conditions):
        self.subconditions = []

        self_type = type(self)
        for cond in conditions:
            # Avoiding nesting (like Any(Any(...), ...) --> Any(...))
            conds = cond.subconditions if isinstance(cond, self_type) else [cond]
            self.subconditions += conds

    def __bool__(self):
        return any(self.subconditions)

    def __repr__(self):
        string = ' | '.join(map(repr, self.subconditions))
        return f'({string})'

    def __str__(self):
        try:
            return super().__str__()
        except AttributeError:
            string = ' | '.join(map(str, self.subconditions))
            return f'({string})'


class All(_ConditionContainer, BaseCondition):

    def __init__(self, *conditions):
        self.subconditions = []

        self_type = type(self)
        for cond in conditions:
            # Avoiding nesting (like All(All(...), ...) --> All(...))
            conds = cond.subconditions if isinstance(cond, self_type) else [cond]
            self.subconditions += conds

    def __bool__(self):
        return all(self.subconditions)

    def __repr__(self):
        string = ' & '.join(map(repr, self.subconditions))
        return f'({string})'

    def __str__(self):
        try:
            return super().__str__()
        except AttributeError:
            string = ' & '.join(map(str, self.subconditions))
            return f'({string})'

    def __getitem__(self, val):
        return self.subconditions[val]


class Not(_ConditionContainer, BaseCondition):

    def __init__(self, condition):
        # TODO: rename condition as child
        self.condition = condition

    def __bool__(self):
        return not(self.condition)

    def __repr__(self):
        string = repr(self.condition)
        return f'~{string}'

    def __str__(self):
        try:
            return super().__str__()
        except AttributeError:
            string = str(self.condition)
            return f'~{string}'

    @property
    def subconditions(self):
        return (self.condition,)

    def __iter__(self):
        return iter((self.condition,))
        
    def __invert__(self):
        "inverse of inverse is the actual condition"
        return self.condition

    def __eq__(self, other):
        "Equal operation"
        is_same_class = isinstance(other, type(self))
        if is_same_class:
            return self.condition == other.condition
        else:
            return False


class AlwaysTrue(BaseCondition):
    "Condition that is always true"
    def __bool__(self):
        return True

    def __repr__(self):
        return 'AlwaysTrue'

    def __str__(self):
        try:
            return super().__str__()
        except AttributeError:
            return 'true'


class AlwaysFalse(BaseCondition):
    "Condition that is always false"

    def __bool__(self):
        return False

    def __repr__(self):
        return 'AlwaysFalse'

    def __str__(self):
        try:
            return super().__str__()
        except AttributeError:
            return 'false'


class TimeCondition(BaseCondition):
    """Base class for Time conditions (whether currently is specified time of day)
    """
    # TODO: Replace with IsPeriod
    def __init__(self, *args, **kwargs):
        if hasattr(self, "period_class"):
            self.period = self.period_class(*args, **kwargs)

    def __bool__(self):
        now = datetime.datetime.now()
        return now in self.period

    def estimate_next(self, dt):
        interval = self.period.rollforward(dt)
        return dt - interval.left

    @classmethod
    def from_period(cls, period):
        new = TimeCondition()
        new.period = period
        return new

    def __repr__(self):
        if hasattr(self, "period"):
            return f'<is {repr(self.period)}>'
        else:
            return type(self).__name__

    def __eq__(self, other):
        "Equal operation"
        is_same_class = isinstance(other, type(self))
        if is_same_class:
            return self.period == other.period
        else:
            return False