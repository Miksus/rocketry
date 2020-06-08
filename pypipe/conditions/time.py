from pypipe.time import TimeOfDay, DaysOfWeek, weekend

from .base import BaseCondition

class TimeCondition(BaseCondition):
    """Base class for Time conditions (whether currently is specified time of day)
    """

    def __init__(self, *args, **kwargs):
        if hasattr(self, "period_class"):
            self.period = self.period_class(*args, **kwargs)

    def __bool__(self):
        return self.current_datetime in self.period

    def estimate_next(self, dt):
        interval = self.period.next(dt)
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

class IsTimeOfDay(TimeCondition):
    period_class = TimeOfDay

class IsDaysOfWeek(TimeCondition):
    period_class = DaysOfWeek

is_weekend = TimeCondition.from_period(weekend)