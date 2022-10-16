import calendar
import datetime
import re
from dataclasses import dataclass
from typing import ClassVar, List

import dateutil

from rocketry.core.time.anchor import AnchoredInterval
from rocketry.core.time.base import TimeInterval
from rocketry.pybox.time import datetime_to_dict, to_microseconds
from rocketry.pybox.time.interval import Interval

@dataclass(frozen=True, init=False)
class TimeOfSecond(AnchoredInterval):
    """Time interval anchored to second cycle of a clock

    min: 0 microsecond
    max: 999999 microsecond

    """

    _scope: ClassVar[str] = "second"

    _scope_max: ClassVar[int] = to_microseconds(second=1)
    _unit_resolution: ClassVar[int] = to_microseconds(millisecond=1)
    _unit_names: ClassVar[List[str]] = [str(i) for i in range(1000)] # 00, 01 etc. till 59

    def anchor_float(self, i, **kwargs):
        return to_microseconds(millisecond=i)

    def anchor_int(self, i, **kwargs):
        if not 0 <= i <= 1000:
            raise ValueError(f"Invalid value: {i}. Allowed: 0-1000")
        return super().anchor_int(i, **kwargs)

    def anchor_str(self, s, **kwargs):
        # ie. 30.123
        res = float(s)
        return to_microseconds(millisecond=res)

@dataclass(frozen=True, init=False)
class TimeOfMinute(AnchoredInterval):
    """Time interval anchored to minute cycle of a clock

    min: 0 seconds, 0 microsecond
    max: 59 seconds, 999999 microsecond
    """

    _scope: ClassVar[str] = "minute"

    _scope_max: ClassVar[int] = to_microseconds(minute=1)
    _unit_resolution: ClassVar[int] = to_microseconds(second=1)
    _unit_names: ClassVar[List[str]] = [f"{i:02d}" for i in range(60)] # 00, 01 etc. till 59

    def anchor_float(self, i, **kwargs):
        return to_microseconds(second=i)

    def anchor_int(self, i, **kwargs):
        if not 0 <= i <= 59:
            raise ValueError(f"Invalid value: {i}. Allowed: 0-59")
        return super().anchor_int(i, **kwargs)

    def anchor_str(self, s, **kwargs):
        # ie. 30.123
        res = re.search(r"(?P<second>[0-9][0-9])([.](?P<microsecond>[0-9]{0,6}))?", s, flags=re.IGNORECASE)
        if res:
            res = res.groupdict()
            if res["microsecond"] is not None:
                res["microsecond"] = res["microsecond"].ljust(6, "0")
            return to_microseconds(**{key: int(val) for key, val in res.items() if val is not None})


@dataclass(frozen=True, init=False)
class TimeOfHour(AnchoredInterval):
    """Time interval anchored to hour cycle of a clock

    min: 0 minutes, 0 seconds, 0 microsecond
    max: 59 minutes, 59 seconds, 999999 microsecond

    Example:
        # From 15 past to half past
        TimeOfHour("15:00", "30:00")
    """
    _scope: ClassVar[str] = "hour"
    _scope_max: ClassVar[int] = to_microseconds(hour=1)
    _unit_resolution: ClassVar[int] = to_microseconds(minute=1)
    _unit_names: ClassVar[List[str]] = [f"{i:02d}:00" for i in range(60)] # 00:00, 01:00 etc. till 59:00

    def anchor_int(self, i, **kwargs):
        if not 0 <= i <= 59:
            raise ValueError(f"Invalid minute: {i}. Minute is from 0 to 59")
        return super().anchor_int(i, **kwargs)

    def anchor_str(self, s, **kwargs):
        # ie. 12:30.123
        res = re.search(r"(?P<minute>[0-9][0-9]):(?P<second>[0-9][0-9])([.](?P<microsecond>[0-9]{0,6}))?", s, flags=re.IGNORECASE)
        if res:
            res = res.groupdict()
            if res["microsecond"] is not None:
                res["microsecond"] = res["microsecond"].ljust(6, "0")
            return to_microseconds(**{key: int(val) for key, val in res.items() if val is not None})

        res = re.search(r"(?P<n>[0-4]) ?(quarter|q)", s, flags=re.IGNORECASE)
        if res:
            # ie. "1 quarter"
            n_quarters = int(res["n"])
            return (self._scope_max + 1) / 4 * n_quarters - 1
        raise ValueError(f"Invalid value: {repr(s)}")

@dataclass(frozen=True, init=False)
class TimeOfDay(AnchoredInterval):
    """Time interval anchored to day cycle of a clock

    min: 0 hours, 0 minutes, 0 seconds, 0 microsecond
    max: 23 hours, 59 minutes, 59 seconds, 999999 microsecond

    Example:
        # From 10 o'clock to 15 o'clock
        TimeOfDay("10:00", "15:00")
    """
    _scope: ClassVar[str] = "day"
    _scope_max: ClassVar[int] = to_microseconds(day=1)
    _unit_resolution: ClassVar[int] = to_microseconds(hour=1)
    _unit_names: ClassVar[List[str]] = [f"{i:02d}:00" for i in range(24)] # 00:00, 01:00, 02:00 etc. till 23:00

    def anchor_int(self, i, **kwargs):
        if not 0 <= i <= 23:
            raise ValueError(f"Invalid hour: {i}. Day is from 00 to 23")
        return super().anchor_int(i, **kwargs)

    def anchor_str(self, s, **kwargs):
        # ie. "10:00:15"
        dt = dateutil.parser.parse(s)
        d = datetime_to_dict(dt)
        components = ("hour", "minute", "second", "microsecond")
        return to_microseconds(**{key: int(val) for key, val in d.items() if key in components})

    def anchor_dt(self, dt, **kwargs):
        "Turn datetime to microseconds according to the scope (by removing higher time elements)"
        d = datetime_to_dict(dt)
        d = {
            key: val
            for key, val in d.items()
            if key in ("hour", "minute", "second", "microsecond")
        }
        return to_microseconds(**d)

@dataclass(frozen=True, init=False)
class TimeOfWeek(AnchoredInterval):
    """Time interval anchored to week cycle

    min: Monday, 0 hours, 0 minutes, 0 seconds, 0 microsecond
    max: Sunday, 23 hours, 59 minutes, 59 seconds, 999999 microsecond

    Example:
        # From Monday 3 PM to Wednesday 4 PM
        TimeOfWeek("Mon 15:00", "Wed 16:00")
    """
    _scope: ClassVar[str] = "week"
    _scope_max: ClassVar[int] = to_microseconds(day=7) # Sun day end of day
    _unit_resolution: ClassVar[int] = to_microseconds(day=1)
    _unit_names: ClassVar[List[str]] = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    _unit_mapping = {
        **dict(zip(range(1, 8), range(7))),

        # English
        **{
            day: i
            for i, day in enumerate(['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'])
        },
        **{
            day: i
            for i, day in enumerate(['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'])
        },
    }

    def anchor_int(self, i, **kwargs):
        # The axis is from 0 to 6 times microseconds per day
        # but if start/end is passed as int, it's considered from 1-7
        # (Monday is 1)
        if not 1 <= i <= 7:
            raise ValueError("Invalid day of week. Week day is from 1 (Monday) to 7 (Sunday).")
        return super().anchor_int(i-1, **kwargs)

    def anchor_str(self, s, side=None, **kwargs):
        # Allowed:
        #   "Mon", "Monday", "Mon 10:00:00"
        res = re.search(r"(?P<dayofweek>[a-z]+) ?(?P<time>.*)", s, flags=re.IGNORECASE)
        comps = res.groupdict()
        dayofweek = comps.pop("dayofweek")
        time = comps.pop("time")
        try:
            nth_day = self._unit_mapping[dayofweek.lower()]
        except KeyError:
            raise ValueError(f"Invalid day of week: {dayofweek}")

        # TODO: TimeOfDay.anchor_str as function
        if not time:
            microseconds = to_microseconds(day=1) if side == "end" else 0
        else:
            microseconds = TimeOfDay().anchor_str(time)

        return to_microseconds(day=1) * nth_day + microseconds

    def anchor_dt(self, dt, **kwargs):
        "Turn datetime to microseconds according to the scope (by removing higher time elements)"
        d = datetime_to_dict(dt)
        d = {
            key: val
            for key, val in d.items()
            if key in ("hour", "minute", "second", "microsecond")
        }
        dayofweek = dt.weekday()
        return to_microseconds(**d) + dayofweek * to_microseconds(day=1)


@dataclass(frozen=True, init=False)
class TimeOfMonth(AnchoredInterval):
    """Time interval anchored to day cycle of a clock

    min: first day of month, 0 hours, 0 minutes, 0 seconds, 0 microsecond
    max: last day of month, 23 hours, 59 minutes, 59 seconds, 999999 microsecond

    Example:
        # From 10 o'clock to 15 o'clock
        TimeOfMonth("1st", "5th")
    """
    # TODO: Support for month end (ie. last 5th day of month to last 2nd)
    # Could be implemented by allowing minus _start and minus _end
    #   rollforward/rollback/contains would need slight changes

    _scope: ClassVar[str] = "year"
    _scope_max: ClassVar[int] = to_microseconds(day=31) # 31st end of day
    _unit_resolution: ClassVar[int] = to_microseconds(day=1)
    _unit_names: ClassVar[List[str]] = ["1st", "2nd", "3rd"] + [f"{i}th" for i in range(4, 32)]
     # NOTE: Floating
    # TODO: ceil end and implement reversion (last 5th day)

    def anchor_int(self, i, **kwargs):
        if not 1 <= i <= 31:
            raise ValueError("Invalid day of month. Day of month can be from 1 to 31")
        # We allow passing days from 1-31 but the axis is built on starting from zero
        i -= 1
        return super().anchor_int(i, **kwargs)

    def anchor_str(self, s, side=None, **kwargs):
        # Allowed:
        #   "5th", "1st", "5", "3rd 12:30:00"
        #   TODO: "first 5th", "last 5th", "last 3rd 10:00:00"
        res = re.search(r"(?P<dayofmonth>[0-9]+)(st|nd|rd|th|[.])? ?(?P<time>.*)", s, flags=re.IGNORECASE)
        comps = res.groupdict()
        dayofmonth = comps.pop("dayofmonth")
        time = comps.pop("time")
        nth_day = int(dayofmonth)

        # TODO: TimeOfDay.anchor_str as function
        ceil_time = not time and side == "end"
        if ceil_time:
            # If time is not defined and the end
            # is being anchored, the time is ceiled.

            # If one says 'thing X was organized between
            # 15th and 17th of July', the sentence
            # includes 17th till midnight.
            microseconds = to_microseconds(day=1)
        elif time:
            microseconds = TimeOfDay().anchor_str(time)
        else:
            microseconds = 0

        return to_microseconds(day=1) * (nth_day - 1) + microseconds

    def anchor_dt(self, dt, **kwargs):
        "Turn datetime to microseconds according to the scope (by removing higher time elements)"
        d = datetime_to_dict(dt)
        d = {
            key: val
            for key, val in d.items()
            if key in ("day", "hour", "minute", "second", "microsecond")
        }
        if "day" in d:
            # Day (of month) does not start from 0 (but from 1)
            d["day"] = d["day"] - 1

        return to_microseconds(**d)

    def get_scope_forward(self, dt):
        n_days = calendar.monthrange(dt.year, dt.month)[1]
        return to_microseconds(day=1) * n_days

    def get_scope_back(self, dt):
        month = 12 if dt.month == 1 else dt.month - 1
        year = dt.year - 1 if dt.month == 1 else dt.year
        n_days = calendar.monthrange(year, month)[1]
        return to_microseconds(day=1) * n_days

@dataclass(frozen=True, init=False)
class TimeOfYear(AnchoredInterval):
    """Time interval anchored to day cycle of a clock

    min: 1st Jan, 0 hours, 0 minutes, 0 seconds, 0 microsecond
    max: 31st Dec, 23 hours, 59 minutes, 59 seconds, 999999 microsecond

    Example:
        # From 10 o'clock to 15 o'clock
        TimeOfYear("Jan", "Feb")
    """

    # We take the longest year there is and translate all years to that
    # using first the month and then the day of month

    _scope: ClassVar[str] = "year"
    _scope_max: ClassVar[int] = to_microseconds(day=1) * 366
    _unit_names: ClassVar[List[str]] = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    _unit_mapping: ClassVar = {
        **dict(zip(range(12), range(12))),

        # English
        **{day.lower(): i for i, day in enumerate(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])},
        **{day.lower(): i for i, day in enumerate(_unit_names)},
    }

    _month_start_mapping: ClassVar = {
        0: 0, # January
        1: to_microseconds(day=31), # February (31 days from year start)
        2: to_microseconds(day=60), # March (31 + 29, leap year has 29 days in February)
        3: to_microseconds(day=91), # April (31 + 29 + 31)
        4: to_microseconds(day=121), # May (31 + 29 + 31 + 30)
        5: to_microseconds(day=152), # June
        6: to_microseconds(day=182), # July
        7: to_microseconds(day=213), # August

        8: to_microseconds(day=244), # September
        9: to_microseconds(day=274), # October
        10: to_microseconds(day=305), # November
        11: to_microseconds(day=335), # December
        12: to_microseconds(day=366), # End of the year (on leap years)
    }
    # Reverse the _month_start_mapping to microseconds to month num
    _year_start_mapping: ClassVar = dict((v, k) for k, v in _month_start_mapping.items())

    # NOTE: Floating

    def anchor_str(self, s, side=None, **kwargs):
        # Allowed:
        #   "January", "Dec", "12", "Dec last 5th 10:00:00"
        res = re.search(r"(?P<monthofyear>[a-z]+) ?(?P<day_of_month>.*)", s, flags=re.IGNORECASE)
        comps = res.groupdict()
        monthofyear = comps.pop("monthofyear") # This is jan, january
        day_of_month_str = comps.pop("day_of_month")
        nth_month = self._unit_mapping[monthofyear.lower()]

        ceil_time = not day_of_month_str and side == "end"
        if ceil_time:
            # If time is not defined and the end
            # is being anchored, the time is ceiled.

            # If one says 'thing X was organized between
            # May and June', the sentence includes
            # time between 1st of May to 30th of June.
            return self._month_start_mapping[nth_month+1] - 1
        if day_of_month_str:
            microseconds = TimeOfMonth().anchor_str(day_of_month_str)
        else:
            microseconds = 0

        return self._month_start_mapping[nth_month] + microseconds

    def to_timepoint(self, ms:int):
        "Turn microseconds to the period's timepoint"
        # Ie. Monday --> Monday 00:00 to Monday 24:00
        # By default assumes linear scale (like week)
        # but can be overridden for non linear such as year
        month_num = self._year_start_mapping[ms]
        return self._month_start_mapping[month_num + 1] - 1

    def anchor_int(self, i, side=None, **kwargs):
        # i is the month (Jan = 1)
        # The axis is from 0 to 365 * microseconds per day
        if not 1 <= i <= 12:
            raise ValueError(f"Invalid month: {i} (Jan is 1 and Dec is 12)")
        i -= 1
        if side == "end":
            return self._month_start_mapping[i+1] - 1
        return self._month_start_mapping[i]

    def anchor_dt(self, dt, **kwargs):
        "Turn datetime to microseconds according to the scope (by removing higher time elements)"
        dt_dict = datetime_to_dict(dt)
        d = {
            key: val
            for key, val in dt_dict.items()
            if key in ("day", "hour", "minute", "second", "microsecond")
        }
        nth_month = dt_dict["month"] - 1
        if "day" in d:
            # Day (of month) does not start from 0 (but from 1)
            d["day"] = d["day"] - 1
        return self._month_start_mapping[nth_month] + to_microseconds(**d)


@dataclass(frozen=True, init=False)
class RelativeDay(TimeInterval):
    """Specific day

    Examples:
    ---------
        Day("today")
        Day("yesterday")
        Day("yesterday")
    """

    offsets: ClassVar = {
        "today": datetime.timedelta(),
        "yesterday": datetime.timedelta(days=1),
        "the_day_before":datetime.timedelta(days=2),
        #"first_day_of_year": get_first_day_of_year,
    }

    min_time: ClassVar[datetime.time] = datetime.time.min
    max_time: ClassVar[datetime.time] = datetime.time.max

    def __init__(self, day, *, start_time=None, end_time=None):
        object.__setattr__(self, "day", day)
        object.__setattr__(self, "start_time", self.min_time if start_time is None else start_time)
        object.__setattr__(self, "end_time", self.max_time if end_time is None else end_time)

    def rollback(self, dt):
        offset = self.offsets[self.day]
        dt -= offset
        return Interval(
            datetime.datetime.combine(dt, self.start_time),
            datetime.datetime.combine(dt, self.end_time)
        )

    def rollforward(self, dt):
        raise AttributeError("RelativeDay has no next day")

    def __repr__(self):
        args_str = str(self.day)
        if self.start_time != self.min.date():
            args_str += f', start_time={self.start_time}'
        if self.end_time != self.max.date():
            args_str += f', end_time={self.end_time}'

        return f"RelativeDay({args_str})"
