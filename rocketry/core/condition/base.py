from copy import copy
from abc import abstractmethod
from typing import Callable, Dict, Pattern, Union

from rocketry._base import RedBase
from rocketry.core.parameters.parameters import Parameters

PARSERS: Dict[Union[str, Pattern], Union[Callable, 'BaseCondition']] = {}


class BaseCondition(RedBase):
    """A condition is a thing/occurence that should happen in
    order to something happen.

    Conditions are used to determine whether a task can be started,
    a task should be terminated or the scheduler should shut
    down. Conditions are either true or false.

    A condition could answer for any of the following questions:
        - Current time is as specified (ie. Monday afternoon).
        - A given task has already run.
        - The machine has at least a given amount of RAM.
        - A specific file exists.

    Each condition should have the method ``__bool__`` specified
    as minimum. This method should return ``True`` or ``False``
    depending on whether the condition holds or does not hold.

    Examples
    --------

    Minimum example:

    >>> from rocketry.core import BaseCondition
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
    >>> from rocketry.parse import parse_condition
    >>> parse_condition("is foo 'bar'")
    IsFooBar('bar')

    """

    def observe(self, **kwargs):
        "Observe the status of the condition"
        cond_params = Parameters._from_signature(self.get_state, **kwargs)
        param_dict = cond_params.materialize(**kwargs)
        return self.get_state(**param_dict)

    def __bool__(self) -> bool:
        """Check whether the condition holds."""
        return self.observe()

    @abstractmethod
    def get_state(self):
        """Get the status of the condition
        (using arguments)

        Override this method."""

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
        if is_same_class:
            # Check equality of the attributes except
            # those that are only for display purposes
            repr_attrs = ("_str",)
            self_dict = {
                key: val for key, val in self.__dict__.items()
                if key not in repr_attrs
            }
            other_dict = {
                key: val for key, val in other.__dict__.items()
                if key not in repr_attrs
            }
            return self_dict == other_dict
        return False

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        raise AttributeError(f"Condition {type(self)} is missing __str__.")


class _ConditionContainer:
    "Wraps another condition"

    def __getitem__(self, val):
        return self.subconditions[val]

    def __iter__(self):
        return iter(self.subconditions)

    def __eq__(self, other):
        "Equal operation"
        is_same_class = isinstance(other, type(self))
        if is_same_class:
            return self.subconditions == other.subconditions
        return False

    def __repr__(self):
        string = ', '.join(map(str, self.subconditions))
        return f'{type(self).__name__}({string})'

class Any(_ConditionContainer, BaseCondition):

    def __init__(self, *conditions):
        self.subconditions = []

        self_type = type(self)
        for cond in conditions:
            # Avoiding nesting (like Any(Any(...), ...) --> Any(...))
            conds = cond.subconditions if isinstance(cond, self_type) else [cond]
            self.subconditions += conds

    def observe(self, **kwargs) -> bool:
        for subcond in self.subconditions:
            if subcond.observe(**kwargs):
                return True
        return False

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

    def observe(self, **kwargs) -> bool:
        for subcond in self.subconditions:
            if not subcond.observe(**kwargs):
                return False
        return True

    def __str__(self):
        try:
            return super().__str__()
        except AttributeError:
            string = ' & '.join(map(str, self.subconditions))
            return f'({string})'


class Not(_ConditionContainer, BaseCondition):

    def __init__(self, condition):
        # TODO: rename condition as child
        self.condition = condition

    def observe(self, **kwargs):
        return not self.condition.observe(**kwargs)

    def __repr__(self):
        string = repr(self.condition)
        return f'Not({string})'

    def __str__(self):
        try:
            return super().__str__()
        except AttributeError:
            string = str(self.condition)
            return f'~{string}'

    @property
    def subconditions(self):
        return (self.condition,)

    def __invert__(self):
        "inverse of inverse is the actual condition"
        return self.condition

    def __eq__(self, other):
        "Equal operation"
        if isinstance(other, AlwaysTrue):
            return isinstance(self.condition, AlwaysFalse)
        if isinstance(other, AlwaysFalse):
            return isinstance(self.condition, AlwaysTrue)

        is_same_class = isinstance(other, type(self))
        if is_same_class:
            return self.condition == other.condition
        return False


class AlwaysTrue(BaseCondition):
    "Condition that is always true"
    def observe(self, **kwargs):
        return True

    def __repr__(self):
        return 'true'

    def __str__(self):
        return 'true'

class AlwaysFalse(BaseCondition):
    "Condition that is always false"

    def observe(self, **kwargs):
        return False

    def __repr__(self):
        return 'false'

    def __str__(self):
        return 'false'


class BaseComparable(BaseCondition):

    _comp_attrs = ("__eq__", "__ne__", "__lt__", "__gt__", "__le__", "__ge__")

    def __init__(self):
        self._comps = {}
        super().__init__()

    def observe(self, **kwargs):
        params = Parameters._from_signature(self.get_measurement, **kwargs)
        param_dict = params.materialize(**kwargs)
        value = self.get_measurement(**param_dict)
        if isinstance(value, bool):
            # Possibly has some optimization and already did the comparison
            return value
        return self.get_state(value)

    @abstractmethod
    def get_measurement(self):
        "Get measurement (something that can be compared)"

    def get_state(self, res:int):
        compares = self._comps

        res = len(res) if hasattr(res, "__len__") else res

        if not compares:
            return res > 0
        return all(
            getattr(res, comp)(val) # Comparison is magic method (==, !=, etc.)
            for comp, val in compares.items()
        )

    def _is_any_over_zero(self):
        # Useful for optimization: just find any observation and the statement is true
        comps = {
            comp: self._comps[comp]
            for comp in self._comp_attrs
            if comp in self._comps
        }
        if comps in ({'__gt__': 0}, {'__ge__': 1}, {'__gt__': 0, '__ge__': 1}):
            return True
        return not comps

    def _is_equal_zero(self):
        comps = {
            comp: self._comps[comp]
            for comp in self._comp_attrs
            if comp in self._comps
        }
        return comps == {"__eq__": 0}

    def __eq__(self, other):
        # self == other
        is_same_class = isinstance(other, BaseCondition)
        if is_same_class:
            # Not storing as parameter to statement but
            # check whether the statements are same
            return super().__eq__(other)
        return self._set_comparison("__eq__", other)

    def __ne__(self, other):
        # self != other
        return self._set_comparison("__ne__", other)

    def __lt__(self, other):
        # self < other
        return self._set_comparison("__lt__", other)

    def __gt__(self, other):
        # self > other
        return self._set_comparison("__gt__", other)

    def __le__(self, other):
        # self <= other
        return self._set_comparison("__le__", other)

    def __ge__(self, other):
        # self >= other
        return self._set_comparison("__ge__", other)

    def _set_comparison(self, key, val):
        obj = copy(self)
        obj._comps[key] = val
        return obj

    @classmethod
    def from_magic(cls, **kwargs):
        for key in kwargs:
            if key not in cls._comp_attrs:
                raise ValueError(f"Unknown comparison: {key}")
        obj = cls()
        obj._comps = kwargs
        return obj
