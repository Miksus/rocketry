import datetime
from rocketry.args.builtin import ReferenceTime

from rocketry.time import TimeDelta
from rocketry.core.condition.base import BaseCondition
from rocketry.core.time.utils import get_period_span

class InPeriod(BaseCondition):
    """Whether given reference date is in the period"""
    def __init__(self, period):
        self.period = period

    def get_state(self, reference:datetime.datetime=ReferenceTime()):
        start, end = get_period_span(self.period)
        return start <= reference <= end

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        if hasattr(self, "period"):
            return f'currently {str(self.period)}'
        return type(self).__name__

    def __repr__(self):
        cls_name = type(self).__name__
        return f"{cls_name}(period={repr(self.period)})"


class IsPeriod(BaseCondition):
    """Condition for checking whether current time
    is in the given time period.

    Parameters
    ----------
    period : rocketry.core.time.TimePeriod
        Time period to check.

    Examples
    --------

    **Parsing example:**

    >>> from rocketry.parse import parse_condition
    >>> parse_condition("time of day between 10:00 and 15:00")
    IsPeriod(period=TimeOfDay('10:00', '15:00'))

    **Construction example:**

    >>> from rocketry.conditions import IsPeriod
    >>> from rocketry.time import TimeOfDay
    >>> is_morning = IsPeriod(period=TimeOfDay("06:00", "12:00")) # doctest: +SKIP
    """
    def __init__(self, period):
        if isinstance(period, TimeDelta):
            raise AttributeError("TimeDelta does not have __contains__.")
        self.period = period

    def get_state(self):
        return datetime.datetime.now() in self.period

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        if hasattr(self, "period"):
            return f'currently {str(self.period)}'
        return type(self).__name__

    def __repr__(self):
        cls_name = type(self).__name__
        return f"{cls_name}(period={repr(self.period)})"
