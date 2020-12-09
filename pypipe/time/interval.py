
import datetime
import calendar

from .base import TimeInterval, register_class

from .utils import floor_time, ceil_time, to_dict, to_nanoseconds, timedelta_to_str

from .anchor import AnchoredInterval, MinuteMixin, HourMixin, DayMixin, WeekMixin, MonthMixin, YearMixin

import pandas as pd
import re
import dateutil

# Pandas
class OffsetInterval(TimeInterval):
    """Base for interval constructed from pandas.offsets
    """
    def __init__(self, offset):
        self.offset = offset

    def __contains__(self, dt):
        # is_on_offset may return np.bool_ type which
        # acts a bit differently than Python bool
        # thus forced to bool
        return bool(self.offset.is_on_offset(dt))

    def rollstart(self, dt):
        "Roll forward till the next start datetime (if not already)"
        return self.offset.rollforward(dt)

    def rollend(self, dt):
        return self.offset.rollback(dt)

    def next_start(self, dt):
        # TODO: Is this needed?
        return dt + self.offset

    def previous(self, dt):
        # TODO: Is this needed?
        return dt - self.offset



# TODO
#   TimeOf... should maybe be cycles?
#   Interval with same logic could be SpanOf

class TimeOfMinute(MinuteMixin, AnchoredInterval):
    """Time interval anchored to minute cycle of a clock

    Example:
        # From 5th second of a minute to 30th second of a minute
        TimeOfHour("5:00", "30:00")
    """

class TimeOfHour(HourMixin, AnchoredInterval):
    """Time interval anchored to hour cycle of a clock

    Example:
        # From 15 past to half past
        TimeOfHour("15:00", "30:00")
    """
    _scope = "hour"
    _scope_max = to_nanoseconds(hour=1)

class TimeOfDay(DayMixin, AnchoredInterval):
    """Time interval anchored to day cycle of a clock
    
    Example:
        # From 10 o'clock to 15 o'clock
        TimeOfDay("10:00", "15:00")
    """

class TimeOfWeek(WeekMixin, AnchoredInterval):
    """Time interval anchored to day cycle of a clock
    
    Example:
        # From 10 o'clock to 15 o'clock
        TimeOfWeek("Mon 15:15", "Wed")
    """

class TimeOfMonth(MonthMixin, AnchoredInterval):
    """Time interval anchored to day cycle of a clock
    
    Example:
        # From 10 o'clock to 15 o'clock
        TimeOfMonth("1st", "5th")
    """

class TimeOfYear(YearMixin, AnchoredInterval):
    """Time interval anchored to day cycle of a clock
    
    Example:
        # From 10 o'clock to 15 o'clock
        TimeOfYear("Jan", "Feb")
    """

# TODO: Add TimeOfWeek, TimeOfMonth, TimeOfYear the same way

class TimeOfDay2(OffsetInterval):

    """Time of Day, ie. from 11:00 to 15:00
    """

    def __init__(self, start, end):
        # NOTE: CustomBusinessHour does allow only HH:MM and not seconds or smaller units
        # Whether seconds or smaller are needed with TimeOfDay is questionable. The scheduler is not meant for extremely time critical stuff.
        self.offset = pd.offsets.CustomBusinessHour(start=start, end=end, weekmask=[1,1,1,1,1,1,1])

    def __invert__(self):
        return TimeOfDay(start=self.end, end=self.start)

    @property
    def is_overnight(self):
        "Whether the interval goes over night (like from 22:00 --> 03:00)"
        return self.offset.start[0] > self.offset.end[0]

    def next_start(self, dt):
        start_time = self.offset.start[0]

        if dt.time() < start_time:
            # not in period, over night
            #                     dt
            #  -->----------<----------->--------------<-
            #  start   |   end        start     |     end

            # not in period, earlier than start
            #          dt                              
            # --<---------->-----------<-------------->--
            #  end   |   start        end    |      start
            
            # in period, over night, earlier than start
            #            dt
            #  -->----------<----------->--------------<-
            #  start   |   end        start     |     end
            pass
        else:
            # not in period, later than start
            #      dt             
            # --<---------->-----------<-------------->--
            #  end   |   start        end    |      start

            # in period, over night, later than start
            #       dt
            #  -->----------<----------->--------------<-
            #  start   |   end        start     |     end

            # in period
            #                    dt             
            # --<---------->-----------<-------------->--
            #  end   |   start        end    |      start
            dt = dt + pd.offsets.Day()
        return pd.Timestamp.combine(dt, start_time)

    def next_end(self, dt):
        end_time = self.offset.end[0]

        if dt.time() <= end_time:
            # in period
            #                    dt             
            # --<---------->-----------<-------------->--
            #  end   |   start        end    |      start
            
            # in period, over night, earlier than end
            #            dt
            #  -->----------<----------->--------------<-
            #  start   |   end        start     |     end

            # not in period, earlier than end
            #          dt                              
            # --<---------->-----------<-------------->--
            #  end   |   start        end    |      start
            pass
        else:
            # not in period, over night
            #                     dt
            #  -->----------<----------->--------------<-
            #  start   |   end        start     |     end

            # not in period, later than end
            #      dt             
            # --<---------->-----------<-------------->--
            #  end   |   start        end    |      start

            # in period, over night, later than end
            #       dt
            #  -->----------<----------->--------------<-
            #  start   |   end        start     |     end
            dt = dt + pd.offsets.Day()

        return pd.Timestamp.combine(dt, end_time)

    def prev_start(self, dt):
        start_time = self.offset.start[0]

        if dt.time() < start_time:
            # not in period, over night
            #                     dt
            #  -->----------<----------->--------------<-
            #  start   |   end        start     |     end

            # not in period, earlier than start
            #          dt                              
            # --<---------->-----------<-------------->--
            #  end   |   start        end    |      start
            
            # in period, over night, earlier than start
            #            dt
            #  -->----------<----------->--------------<-
            #  start   |   end        start     |     end
            dt = dt - pd.offsets.Day()
        else:
            # not in period, later than start
            #      dt             
            # --<---------->-----------<-------------->--
            #  end   |   start        end    |      start

            # in period, over night, later than start
            #       dt
            #  -->----------<----------->--------------<-
            #  start   |   end        start     |     end

            # in period
            #                    dt             
            # --<---------->-----------<-------------->--
            #  end   |   start        end    |      start
            pass
        return pd.Timestamp.combine(dt, start_time)

    def prev_end(self, dt):
        end_time = self.offset.end[0]

        if dt.time() < end_time:
            # in period
            #                    dt             
            # --<---------->-----------<-------------->--
            #  end   |   start        end    |      start
            
            # in period, over night, earlier than end
            #            dt
            #  -->----------<----------->--------------<-
            #  start   |   end        start     |     end

            # not in period, earlier than end
            #          dt                              
            # --<---------->-----------<-------------->--
            #  end   |   start        end    |      start
            dt = dt - pd.offsets.CDay()
        else:
            # not in period, over night
            #                     dt
            #  -->----------<----------->--------------<-
            #  start   |   end        start     |     end

            # not in period, later than end
            #      dt             
            # --<---------->-----------<-------------->--
            #  end   |   start        end    |      start

            # in period, over night, later than end
            #       dt
            #  -->----------<----------->--------------<-
            #  start   |   end        start     |     end
            pass

        return pd.Timestamp.combine(dt, end_time)

    @property
    def start(self):
        return self.offset.start[0]

    @property
    def end(self):
        return self.offset.end[0]

    def __repr__(self):
        return f'TimeOfDay({self.start}, {self.end})'

    @classmethod
    def from_between(cls, start, end):
        return cls(start, end)

class DaysOfWeek(OffsetInterval):
    """Day of Week, ie. Monday, Tuesday and Saturday
    """

    def __init__(self, *weekdays, **kwargs):
        # TODO: Start & end
        weekmask = self.get_weekmask(*weekdays, start=kwargs.pop("start", None), end=kwargs.pop("end", None))
        self.offset = pd.offsets.CustomBusinessDay(weekmask=weekmask)
        # self.conditions = (DayOfWeek(weekday) for weekday in weekdays)

    def __invert__(self):
        weekmask = [{1:0, 0:1}[d] for d in self.offset.weekmask]
        return DaysOfWeek(weekmask)

    def get_weekmask(self, *values, start=None, end=None):
        "Turn values to week mask (ie. Tuesday & Thursday --> [0, 1, 0, 1, 0, 0, 0])"
        if values:
            return self._get_weekmask_from_values(*values)
        else:
            return self._get_weekmask_from_span(start=start, end=end)

    def _get_weekmask_from_span(self, start, end):

        start = 0 if start is None else start
        end = 6 if end is None else end
        
        start = start.capitalize() if isinstance(start, str) else start
        end = end.capitalize() if isinstance(end, str) else end

        weeknum_mapping = {
            **dict(zip(calendar.day_name, range(7))), 
            **dict(zip(calendar.day_abbr, range(7))), 
            **dict(zip(range(7), range(7)))
        }

        start = weeknum_mapping[start]
        end = weeknum_mapping[end] + 1

        weekmask = [0] * 7
        weekmask[slice(start, end)] = [1] * len(range(start, end))
        return weekmask

    def _get_weekmask_from_values(self, *values):
        "Turn values to week mask (ie. Tuesday & Thursday --> [0, 1, 0, 1, 0, 0, 0])"
        if len(values) == 7 and all(val in (0, 1) for val in values):
            # Already binary
            return values
        
        weekdays_binary = []

        weekday_abbrs = list(calendar.day_abbr)
        weekday_names = list(calendar.day_name)

        if isinstance(values, (list, tuple, set)):
            for i in range(7):
                if weekday_abbrs[i] in values or weekday_names[i] in values or i in values:
                    weekdays_binary.append(1)
                else:
                    weekdays_binary.append(0)
        else:
            return values

        return weekdays_binary

    @property
    def weekdays(self):
        mapping = dict(zip(range(7), list(calendar.day_abbr)))
        return [
            mapping[i] 
            for i, val in enumerate(self.offset.weekmask)
            if val
        ]

    def __repr__(self):
        string = ', '.join(self.weekdays)
        return f'<{string}>'

    def rollstart(self, dt):
        dt_rolled = super().rollstart(dt)
        return floor_time(dt_rolled) if dt_rolled != dt else dt_rolled

    def rollend(self, dt):
        dt_rolled = super().rollend(dt)
        return ceil_time(dt_rolled) if dt_rolled != dt else dt_rolled

    def next_end(self, dt):
        # We loop days before we hit a day that 
        # is not on the week mask
        dt = self.rollstart(dt)
        while self.offset.weekmask[(dt + pd.offsets.Day()).weekday()]:
            dt = dt + pd.offsets.Day()
        return ceil_time(dt)

    def prev_start(self, dt):
        # We loop days before we hit a day that 
        # is not on the week mask
        dt = self.rollend(dt)
        while self.offset.weekmask[(dt - pd.offsets.Day()).weekday()]:
            dt = dt - pd.offsets.Day()
        return floor_time(dt)

    @classmethod
    def from_between(cls, start, end):
        weekday_abbrs = list(calendar.day_abbr)
        weekday_names = list(calendar.day_name)
        weekday_list = (
            weekday_abbrs if start in weekday_abbrs and end in weekday_abbrs
            else weekday_names if start in weekday_names and end in weekday_names
            else None
        )
        if weekday_list is None:
            raise ValueError(f"Invalid week days: {start} & {end}")
        start_index = weekday_list.index(start)
        end_index = weekday_list.index(end)
        return cls(*weekday_list[start_index:end_index])

class RelativeDay(TimeInterval):
    """Specific day

    Examples:
    ---------
        Day("today")
        Day("yesterday")
        Day("yesterday")
    """

    offsets = {
        "today": pd.Timedelta("0 day"),
        "yesterday": pd.Timedelta("1 day"),
        "the_day_before": pd.Timedelta("2 day"),
        #"first_day_of_year": get_first_day_of_year,
    }

    def __init__(self, day, *, start_time=None, end_time=None):
        self.day = day
        self.start_time = self.min.date() if start_time is None else start_time
        self.end_time = self.max.date() if end_time is None else end_time

    def rollback(self, dt):
        offset = self.offsets[self.day]
        dt = dt - offset
        return pd.Interval(
            pd.Timestamp.combine(dt, self.start_time),
            pd.Timestamp.combine(dt, self.end_time)
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
