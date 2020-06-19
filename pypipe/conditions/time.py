from pypipe.time import TimeOfDay, DaysOfWeek, weekend

from .base import TimeCondition

from scipy import stats

class IsTimeOfDay(TimeCondition):
    period_class = TimeOfDay

class IsDaysOfWeek(TimeCondition):
    period_class = DaysOfWeek

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

        return self.current_datetime in self.period

    def normal(self, start, end, std, mean=None):
        start_sec = start.timestamp()
        end_sec = end.timestamp()
        if mean is None:
            mean = (left.timestamp() + right.timestamp()) / 2

        a, b = (start_sec - my_mean) / std, (end_sec - my_mean) / std
        return stats.truncnorm(a, b, loc=mean, scale=std)

is_weekend = TimeCondition.from_period(weekend)