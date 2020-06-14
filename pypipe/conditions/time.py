from pypipe.time import TimeOfDay, DaysOfWeek, weekend

from .base import TimeCondition



class IsTimeOfDay(TimeCondition):
    period_class = TimeOfDay

class IsDaysOfWeek(TimeCondition):
    period_class = DaysOfWeek

is_weekend = TimeCondition.from_period(weekend)