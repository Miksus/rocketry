
import calendar
import re

from .base import PERIOD_CLASSES, get_period
from .base import TimeInterval, TimeDelta, TimeCycle

from .cycle import (Weekly, Daily, Hourly, Minutely)
from .interval import DaysOfWeek, TimeOfDay, TimeOfHour


def _get_cycle(type_, start=None):
    type_ = type_.lower()
    cls = {
        "daily": Daily,
        "weekly": Weekly,
        "hourly": Hourly,
        "minutely": Minutely,
    }[type_]
    if start is None:
        return cls()
    elif start.isdigit():
        return cls(int(start))
    else:
        return cls(start)

def _get_interval(type_, start=None, end=None):
    type_ = type_.lower()
    cls = {
        "daily": TimeOfDay,
        "weekly": DaysOfWeek,
        "hourly": TimeOfHour,
    }[type_]
    return cls(start=start, end=end)

def _get_delta(value):
    return TimeDelta(value)

class _PeriodFactory:

    _weekdays = '|'.join(calendar.day_name) + "|" + '|'.join(calendar.day_abbr)

    # Expressions for dynamic string parameters
    expressions = [
        (r"(?P<type_>monthly|weekly|daily|hourly|minutely) starting (?P<start>.+)", _get_cycle),
        # (r"(?P<type_>monthly|weekly|daily|hourly|minutely) ending (?P<end>.+)", _get_cycle),

        (r"(?P<type_>monthly|weekly|daily|hourly|minutely) between (?P<start>.+) and (?P<end>.+)", _get_interval),
        (r"(?P<type_>monthly|weekly|daily|hourly|minutely) after (?P<start>.+)", _get_interval),
        (r"(?P<type_>monthly|weekly|daily|hourly|minutely) before (?P<end>.+)", _get_interval),

        (r"(?P<type_>monthly|weekly|daily|hourly|minutely)", _get_cycle),
        (r"past (?P<value>.+)", _get_delta),
    ]

    cycle_expressions = {

        r"daily at (?P<start>[0-9][0-9]:[0-9][0-9])": Daily, # "daily at 11:00"
        fr"weekly on (?P<start>({_weekdays}))": Weekly, # Intended (not working): "weekly from tuesday"
        # r"monthly on (?P<start>[1-3]?[0-9])": Monthly,
        # fr"yearly on (?P<start>({_months}))": Yearly,
        # fr"yearly on (?P<start_day>[0-3][0-9]\.(?P<start>({_months}))": Yearly,

        # TODO:
        # quarterly from first --> Quarterly(start=1)
        # quarterly from third --> Starts from third quarter (3/4 of hour)
        # hourly at third --> Starts from third quarter (3/4 of hour)
    }
    del _weekdays

    def when(self, s:str):
        """Create time period from a string

        Examples:
        ---------
            _PeriodFactory().when("Monthly starting 5")
            _PeriodFactory().when("Weekly starting monday")
            _PeriodFactory().when("Daily between 11:00 and 15:00")
            _PeriodFactory().when("past 5 hours")
            _PeriodFactory().when("Daily after 13:00")
            _PeriodFactory().when("Daily before 08:00")

        Args:
            s (str): [description]

        Raises:
            ValueError: If construction not found

        Returns:
            [TimePeriod]: [description]
        """
        for expr, func in self.expressions:
            res = re.search(expr, s, flags=re.IGNORECASE)
            if res:
                return func(**res.groupdict())
        else:
            raise ValueError(f"Unknown conversion for: {s}")


    def between(self, start, end):
        """[summary]

        Examples:
        ---------
            # Get period from 08:00 to 15:00
            period_factory.between("08:00", "15:00")
            >>> TimeInterval("08:00", "15:00")

            # Get period from Monday to Tuesday
            period_factory.between("Mon", "Tue")
            >>> TimeInterval("Mon", "Tue")
        """
        clses = PERIOD_CLASSES[TimeInterval]
        for cls in clses:
            try:
                intrv = cls.from_between(start, end)
            except (ValueError, NotImplementedError):
                continue
            else:
                return intrv
        else:
            raise ValueError(f"No interval for {start} and {end}")

    def past(self, *args, **kwargs):
        """[summary]

        Examples:
        ---------
            # Get period of past 1 day and 5 hours
            period_factory.in_("1 day 5 hours")
            >>> TimeDelta("1 day 5 hours")
        """
        return TimeDelta(*args, **kwargs)

    def in_(self, period):
        """[summary]

        Examples:
        ---------
            # Get period of today
            period_factory.in_("today")
            >>> TimeInterval("00:00", "24:00")

            # Get period of weekend
            period_factory.in_("weekend")
            >>> DaysOfWeek("Sat", "Sun")

            # Get period of yesterday
            period_factory.in_("yesterday")
            >>> RelativeDay("yesterday")
        """
        return get_period(period, group="in_")

    def in_cycle(self, cycle):
        """[summary]

        Examples:
        ---------
            # Get cycle starting at today
            period_factory.in_cycle("daily")
            >>> Daily(start="00:00")

            # Get cycle starting at monday
            period_factory.in_cycle("weekly")
            >>> Weekly(start="Monday")
        """
        # TODO: change the PEDIODS to
        # {
        #   "in_": {
        #       "today": TimeOfDay("00:00", "24:00"),
        #       "yesterday": RelativeDay("yesterday")
        #   },
        #   "in_cycle": {
        #       "daily": Daily(),
        #       "weekly": Weekly(),
        #   },
        #   "from_": {
        #       "yesterday": Daily(n=2),
        #       "Monday": Weekly(start="Monday")
        #   }
        # }
        if isinstance(cycle, TimeCycle):
            return cycle
        try:
            return get_period(cycle, group=TimeCycle)()
        except KeyError:
            # Try expressions
            for expr, cls in self.cycle_expressions.items():
                result = re.search(expr, cycle)
                if result is not None:
                    return cls(**result.groupdict())
            else:
                raise ValueError
                

    def from_(self, value):
        """[summary]

        Examples:
        ---------
            # Get period from yesterday to current time
            period_factory.from_("yesterday")
            >>> Daily(n=2)

            # Get period from morning to current time
            period_factory.from_("morning")
            >>> Daily(start="08:00")

            # Get period from monday to current time
            period_factory.from_("Monday")
            >>> Weekly(start="Monday")
        """
        return get_period(value, group="from_")

period_factory = _PeriodFactory()