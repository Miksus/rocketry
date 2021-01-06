
import calendar
import datetime
import pandas as pd

from pypipe.core.time.base import TimeCycle
from pypipe.core.time.anchor import AnchoredCycle, MinuteMixin, HourMixin, DayMixin, WeekMixin, MonthMixin, YearMixin

# TODO: Remove cycles

class PandasPeriod(TimeCycle):
    """Generic Cycle utilizing pandas
    frequencies. 
    """
    offset = None
    def __init__(self, freq=None):
        self.freq = freq

    def rollback(self, dt):
        df_start = pd.Period(dt, freq=self.freq).to_timestamp(how="start")
        return pd.Interval(dt_start, dt)

    def rollforward(self, dt):
        dt_end = pd.Period(dt, freq=self.freq).to_timestamp(how="end")
        return pd.Interval(dt, dt_end)

class Minutely(MinuteMixin, AnchoredCycle):
    # TODO: Test
    """A cycle that starts once in a minute

    Example:
    --------
        Minutely() # Minutely starting from 0 seconds
        Minutely(second=30) # Minutely starting from 30 seconds
    """

class Hourly(HourMixin, AnchoredCycle):
    ""

class Daily(DayMixin, AnchoredCycle):
    ""

class Weekly(WeekMixin, AnchoredCycle):
    ""

class Monthly(MonthMixin, AnchoredCycle):
    ""

class Yearly(YearMixin, AnchoredCycle):
    ""

class Quarterly(TimeCycle):
    # TODO
    """A cycle that starts once in a quarter of an hour

    Example:
    --------
        Quarterly() # Quarterly starting from quarter past
        Quarterly(minute=30) # Hourly starting from half past
    """

    offset = pd.Timedelta("15 minutes")
    start_time = 0
    def transform_start(self, *args, **kwargs):
        return 0 # Offsetting is never needed thus zero provided

    def get_time_element(self, dt):
        return dt.minute % 15

    def replace(self, dt):
        minutes_over = dt.minute % 15
        repl_dict = dict(
            minute=dt.minute - minutes_over,
            second=0,
            microsecond=0,
            nanosecond=0,
        )

        if not hasattr(dt, "nanosecond"):
            repl_dict.pop("nanosecond")

        return dt.replace(**repl_dict)

