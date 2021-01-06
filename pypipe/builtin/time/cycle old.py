
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

    def rollback(self, dt):
        df_start = pd.Period(dt, freq=self.freq).to_timestamp(how="start")
        return pd.Interval(dt_start, dt)

    def rollforward(self, dt):
        dt_end = pd.Period(dt, freq=self.freq).to_timestamp(how="end")
        return pd.Interval(dt, dt_end)

class Minutely(TimeCycle):
    # TODO: Test
    """A cycle that starts once in a minute

    Example:
    --------
        Minutely() # Minutely starting from 0 seconds
        Minutely(second=30) # Minutely starting from 30 seconds
    """

    offset = pd.Timedelta("1 minutes")
    start_time = 0
    def transform_start(self, *args, **kwargs):
        ns = self.to_nanoseconds(*args, **kwargs)
        return ns

    def get_time_element(self, dt):
        ns = self.to_nanoseconds(dt.second, dt.microsecond, dt.nanosecond if hasattr(dt, "nanosecond") else 0)
        return ns

    @staticmethod
    def to_nanoseconds(second=0, microsecond=0, nanosecond=0):
        return nanosecond + microsecond * 1_000 + second * 1_000_000_000

    def replace(self, dt):
        repl_dict = dict(
            second=self.second,
            microsecond=self.microsecond,
            nanosecond=self.nanosecond,
        )

        if not hasattr(dt, "nanosecond"):
            repl_dict.pop("nanosecond")

        return dt.replace(**repl_dict)


    @property
    def second(self):
        return int(self.start / 1_000_000_000)

    @property
    def microsecond(self):
        ns_by_seconds = 1_000_000_000 * self.second
        return int((self.start - ns_by_seconds) / 1_000)

    @property
    def nanosecond(self):
        ns_by_seconds = 1_000_000_000 * self.second
        ns_by_microsecond = 1_000 * self.microsecond
        return int((self.start - ns_by_seconds - ns_by_microsecond))

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


class Hourly(TimeCycle):
    # TODO: Test
    """A cycle that starts once in an hour

    Example:
    --------
        Hourly(minute=15) # Hourly starting from quarter past
        Hourly(minute=30) # Hourly starting from half past
    """

    offset = pd.Timedelta("1 hour")
    start_time = 0
    def transform_start(self, *args, **kwargs):
        ns = self.to_nanoseconds(*args, **kwargs)
        return ns

    def get_time_element(self, dt):
        ns = self.to_nanoseconds(dt.minute, dt.second, dt.microsecond, dt.nanosecond if hasattr(dt, "nanosecond") else 0)
        return ns

    @staticmethod
    def to_nanoseconds(minute=0, second=0, microsecond=0, nanosecond=0):
        return nanosecond + microsecond * 1_000 + second * 1_000_000_000 + minute * 60_000_000_000

    def replace(self, dt):
        repl_dict = dict(
            minute=self.minute,
            second=self.second,
            microsecond=self.microsecond,
            nanosecond=self.nanosecond,
        )

        if not hasattr(dt, "nanosecond"):
            repl_dict.pop("nanosecond")

        return dt.replace(**repl_dict)

    @property
    def minute(self):
        return int(self.start / 60_000_000_000)

    @property
    def second(self):
        ns_by_minutes = 60_000_000_000 * self.minute
        return int((self.start - ns_by_minutes) / 1_000_000_000)

    @property
    def microsecond(self):
        ns_by_minutes = 60_000_000_000 * self.minute
        ns_by_seconds = 1_000_000_000 * self.second
        return int((self.start - ns_by_minutes - ns_by_seconds) / 1_000)

    @property
    def nanosecond(self):
        ns_by_minutes = 60_000_000_000 * self.minute
        ns_by_seconds = 1_000_000_000 * self.second
        ns_by_microsecond = 1_000 * self.microsecond
        return int((self.start - ns_by_minutes - ns_by_seconds - ns_by_microsecond))

class Daily(TimeCycle):
    offset = pd.Timedelta("1 day")

    def transform_start(self, arg=None):
        if arg is None:
            return datetime.time.min
        # This is slight hack. pd.offsets.Timestamp accepts
        # also only time part (ie. pd.offsets.Timestamp("10:00:12"))
        # TODO: Make a check that no date is passed with arg or change pd.offsets.Timestamp to pd.offsets.CustomBusinessHour
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
    start_time = datetime.time.min

    def transform_start(self, arg=None):
        if arg is None:
            return self.mapping[0]
        if hasattr(arg, "weekday"):
            arg = arg.weekday()
        elif isinstance(arg, str):
            # calendar.day_name and calendar.day_abbr both are capitalized thus forcing
            arg = arg.capitalize()
        return self.mapping[arg]

    def get_time_element(self, dt):
        return dt.weekday()

    def replace(self, dt):
        diff = self.start - dt.weekday()
        dt = dt + pd.offsets.Day() * diff
        return pd.Timestamp.combine(dt, self.start_time)

# TODO: This in init
#monthly = Monthly(access_name="monthly")