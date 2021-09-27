
import datetime

from redengine.time import TimeOfDay, TimeOfWeek, TimeDelta
from redengine.time.construct import get_full_cycle, get_between, get_after, get_before
from redengine.core.condition.base import TimeCondition, BaseCondition

class IsPeriod(BaseCondition):
    """Condition for checking whether current time
    is in the given time period. 

    Parameters
    ----------
    period : redengine.core.time.TimePeriod
        Time period to check.

    Examples
    --------

    **Parsing example:**

    >>> from redengine.parse import parse_condition
    >>> parse_condition("time of day between 10:00 and 15:00")
    IsPeriod(period=TimeOfDay('10:00', '15:00'))

    **Construction example:**

    >>> from redengine.conditions import IsPeriod
    >>> from redengine.time import TimeOfDay
    >>> is_morning = IsPeriod(period=TimeOfDay("06:00", "12:00")) # doctest: +SKIP
    """
    def __init__(self, period):
        if isinstance(period, TimeDelta):
            raise AttributeError("TimeDelta does not have __contains__.")
        self.period = period

    def __bool__(self):
        return datetime.datetime.now() in self.period

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        elif hasattr(self, "period"):
            return f'is {str(self.period)}'
        else:
            return type(self).__name__

    def __repr__(self):
        cls_name = type(self).__name__
        return f"{cls_name}(period={repr(self.period)})"

    @classmethod
    def _from_parser(cls, span_type, **kwargs):
        period_func = {
            "between": get_between,
            "after": get_after,
            "before": get_before,
        }[span_type]
        period = period_func(**kwargs)
        return cls(period=period)



class IsTimeOfDay(TimeCondition):
    period_class = TimeOfDay

class IsTimeOfWeek(TimeCondition):
    period_class = TimeOfWeek

class Randomly(TimeCondition):

    def __init__(self, *args, **kwargs):
        if hasattr(self, "period_class"):
            self.period = self.period_class(*args, **kwargs)
    
    def __bool__(self):
        # TODO
        curr_interval = self.period.rollback(dt)
        prev_interval = self._prev_interval

        next_interval = self.period.rollforward(dt)

        if next_interval != self._prev_next_interval:
            start = next_interval.left
            end = next_interval.right

            distr = self.get_distr(start=start, end=end) 
            true_times = distr.rvs(size=self.n)

            self._timestamps = [pd.Timestamp.utcfromtimestamp(time) for time in true_times]

        return datetime.datetime.now() in self.period

    def normal(self, start, end, std, mean=None):
        start_sec = start.timestamp()
        end_sec = end.timestamp()
        if mean is None:
            mean = (left.timestamp() + right.timestamp()) / 2

        a, b = (start_sec - my_mean) / std, (end_sec - my_mean) / std
        return stats.truncnorm(a, b, loc=mean, scale=std)

#is_weekend = TimeCondition.from_period(weekend)