
import datetime
from abc import abstractmethod

from atlas.core import time

class BaseCondition:
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

    """

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

    @property
    def cycle(self):
        "By default, the cycle is all the times"
        # By default the time cycle cannot be determined thus full range is given
        return time.StaticInterval()

    def __eq__(self, other):
        "Equal operation"
        is_same_class = isinstance(other, type(self))
        return is_same_class


class _ConditionContainer:
    "Wraps another condition"

    __magicmethod__ = None

    def flatten(self):
        conditions = []
        for attr in self._cond_attrs:
            conds = getattr(self, attr)

            conditions += conds
        return conditions

    def apply(self, func, **kwargs):
        "Apply the function to all subconditions"
        # TODO: Delete?
        subconds = []
        for subcond in self.subconditions:
            if isinstance(subcond, ConditionContainer):
                subcond = subcond.apply(func, **kwargs)
            else:
                subcond = func(subcond, **kwargs)
            subconds.append(subcond)
        return type(self)(*subconds)
        
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

    __magicmethod__ = "__or__"

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

    @property
    def cycle(self):
        "Aggregate the TimePeriods the condition has"
        all_timeperiods = all(isinstance(cond, TimeCondition) for cond in self.subconditions)
        if all_timeperiods:
            # Can be determined
            return time.Any(*[cond.cycle for cond in self.subconditions])
        else:
            # Cannot be determined --> all times may be valid
            return time.StaticInterval()

class All(_ConditionContainer, BaseCondition):

    __magicmethod__ = "__and__"

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

    def __getitem__(self, val):
        return self.subconditions[val]

    @property
    def cycle(self):
        "Aggregate the TimePeriods the condition has"
        return time.All(*[cond.cycle for cond in self.subconditions])

class Not(_ConditionContainer, BaseCondition):

    __magicmethod__ = "__invert__"

    def __init__(self, condition):
        # TODO: rename condition as child
        self.condition = condition

    def __bool__(self):
        return not(self.condition)

    def __repr__(self):
        string = repr(self.condition)
        return f'~{string}'

    @property
    def subconditions(self):
        return (self.condition,)

    @property
    def cycle(self):
        "Aggregate the TimePeriods the condition has"
        if isinstance(self.condition, TimeCondition):
            # Can be determined
            return ~self.condition.cycle
        else:
            # Cannot be determined --> all times may be valid
            return time.StaticInterval()

#    def __getattr__(self, name):
#        """Called as last resort so the actual 
#        condition's attribute returned to be more
#        flexible"""
#        return getattr(self.condition, name)

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

class AlwaysFalse(BaseCondition):
    "Condition that is always false"
    def __bool__(self):
        return False

    def __repr__(self):
        return 'AlwaysFalse'


class IsPeriod(BaseCondition):
    def __init__(self, period):
        if isinstance(period, time.TimeDelta):
            raise AttributeError("TimeDelta does not have __contains__.")
        self.period = period

    def __bool__(self):
        return datetime.datetime.now() in self.period


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