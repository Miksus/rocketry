
import calendar
import datetime
import pandas as pd

from .base import TimeCycle


class PandasPeriod(TimeCycle):
    """Generic Cycle utilizing pandas
    frequencies. 
    """
    offset = None
    def __init__(self, freq=None):
        self.freq = freq

    def prev(self, dt):
        df_start = pd.Period(dt, freq=self.freq).to_timestamp(how="start")
        return pd.Interval(dt_start, dt)

    def next(self, dt):
        dt_end = pd.Period(dt, freq=self.freq).to_timestamp(how="end")
        return pd.Interval(dt, dt_end)


class Daily(TimeCycle):
    offset = pd.Timedelta("1 day")

    def transform_start(self, arg):
        if arg is None:
            return datetime.time.min
        return pd.offsets.Timestamp(arg).time()

    def get_time_element(self, dt):
        return dt.time()

    def replace(self, dt):
        return pd.Timestamp.combine(dt, self.start)

class Weekly(TimeCycle):
    offset = pd.Timedelta("7 days")

    mapping = {
        **dict(zip(calendar.day_name, range(7))), 
        **dict(zip(calendar.day_abbr, range(7))), 
        **dict(zip(range(7), range(7)))
    }

    def transform_start(self, arg):
        if arg is None:
            return self.mapping[0]
        if hasattr(arg, "weekday"):
            arg = arg.weekday()
        return self.mapping[arg]

    def get_time_element(self, dt):
        return dt.weekday()

    def replace(self, dt):
        diff = self.start - dt.weekday()
        dt + pd.offsets.Day() * diff
        return pd.Timestamp.combine(dt, self.start)

daily = Daily(access_name="daily")
weekly = Weekly(access_name="weekly")
#monthly = Monthly(access_name="monthly")