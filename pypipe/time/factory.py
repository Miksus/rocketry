
import calendar
import re

from .base import PERIOD_CLASSES, get_period
from .base import TimeInterval, TimeDelta, TimeCycle

from .cycle import (Daily, Weekly)


class _PeriodFactory:

    _weekdays = '|'.join(calendar.day_name) + "|" + '|'.join(calendar.day_abbr)
    cycle_expressions = {
        r"daily at (?P<start>[0-9][0-9]:[0-9][0-9])": Daily,
        fr"weekly on (?P<start>({_weekdays}))": Weekly,
        # r"monthly on (?P<start>[1-3]?[0-9])": Monthly,
        # fr"yearly on (?P<start>({_months}))": Yearly,
        # fr"yearly on (?P<start_day>[0-3][0-9]\.(?P<start>({_months}))": Yearly,
    }
    del _weekdays

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
            return get_period(cycle, group="in_cycle")
        except KeyError:
            # Try expressions
            for expr, cls in self.cycle_expressions.items():
                result = re.search(expr, cycle)
                if result is not None:
                    return cls(**result.groupdict())
                

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