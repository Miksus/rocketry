
import datetime
import calendar

from .base import TimeInterval, register_class

from .utils import floor_time, ceil_time, to_dict, to_nanoseconds

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


class AnchoredInterval(TimeInterval):
    """Base for interval for those that have fixed time unit (that can be converted to nanoseconds)
    """
    components = ("year", "month", "day", "hour", "minute", "second", "microsecond", "nanosecond")
    _scope = None # ie. day, hour, second, microsecond

    def __init__(self, start=None, end=None):
        self.start = start
        self.end = end

    def _to_relative_nanoseconds(self, dt):
        "Turn datetime to nanoseconds according to the scope (by removing higher time elements)"
        components = self.components
        components = components[components.index(self._scope) + 1:]
        d = to_dict(dt)
        d = {
            key: val
            for key, val in d.items()
            if key in components
        }

        return to_nanoseconds(**d)

    def __contains__(self, dt):
        ns = self._to_relative_nanoseconds(dt) # In relative nanoseconds (removed more accurate than scope)
        ns_start = self.start_in_nanoseconds
        ns_end = self.end_in_nanoseconds

        is_over_period = ns_start > ns_end
        if not is_over_period:
            return ns_start <= ns <= ns_end
        else:
            return ns >= ns_start or ns <= ns_end

    def rollstart(self, dt):
        "Roll forward to next point in time that on the period"
        if dt in self:
            return dt
        else:
            return self.next_start(dt)

    def rollend(self, dt):
        "Roll back to previous point in time that is on the period"
        if dt in self:
            return dt
        else:
            return self.prev_end(dt)

    def next_start(self, dt):
        "Get next start point of the period"
        ns = self._to_relative_nanoseconds(dt) # In relative nanoseconds (removed more accurate than scope)
        ns_start = self.start_in_nanoseconds
        ns_end = self.end_in_nanoseconds

        if ns < ns_start:
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
            offset = pd.Timedelta(nanoseconds=int(ns_start) - int(ns))
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
            offset = pd.Timedelta(nanoseconds=int(ns_start) - int(ns) + self.period_in_nanoseconds)
        return dt + offset

    def next_end(self, dt):
        "Get next end point of the period"
        ns = self._to_relative_nanoseconds(dt) # In relative nanoseconds (removed more accurate than scope)
        ns_start = self.start_in_nanoseconds
        ns_end = self.end_in_nanoseconds

        if ns <= ns_end:
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
            offset = pd.Timedelta(nanoseconds=int(ns_end) - int(ns))
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
            offset = pd.Timedelta(nanoseconds=int(ns_end) - int(ns) + self.period_in_nanoseconds)
        return dt + offset

    def prev_start(self, dt):
        "Get previous start point of the period"
        ns = self._to_relative_nanoseconds(dt) # In relative nanoseconds (removed more accurate than scope)
        ns_start = self.start_in_nanoseconds
        ns_end = self.end_in_nanoseconds

        if ns < ns_start:
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
            offset = pd.Timedelta(nanoseconds=int(ns_start) - int(ns) - self.period_in_nanoseconds)
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
            offset = pd.Timedelta(nanoseconds=int(ns_start) - int(ns))
        return dt + offset

    def prev_end(self, dt):
        "Get pervious end point of the period"
        ns = self._to_relative_nanoseconds(dt) # In relative nanoseconds (removed more accurate than scope)
        ns_start = self.start_in_nanoseconds
        ns_end = self.end_in_nanoseconds

        if ns < ns_end:
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
            offset = pd.Timedelta(nanoseconds=int(ns_end) - int(ns) - self.period_in_nanoseconds)
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
            offset = pd.Timedelta(nanoseconds=int(ns_end) - int(ns))

        return dt + offset

    @property
    def period_in_nanoseconds(self):
        return int(to_nanoseconds(**{self._scope: 1}))

    @property
    def start_in_nanoseconds(self):
        return self.to_time_element(self.start)

    @property
    def end_in_nanoseconds(self):
        return self.to_time_element(self.end)

    def to_time_element(self, value):

        if isinstance(value, dict):
            # {"hour": 10, "minute": 20}
            components = self.sub_time_components
            if any(key not in components for key in kwargs):
                invalid_comp = [key for key in kwargs if key not in components]
                raise ValueError(f"Items {invalid_comp} not in allowed components")
            return to_nanoseconds(**value)
        elif isinstance(value, int):
            # start is considered as unit of the second behind scope
            component = self.sub_time_components[0]
            return to_nanoseconds(**{component: value})
        elif isinstance(value, str):
            
            if self._scope == "day":
                # ie. "10:00:15"
                dt = dateutil.parser.parse(value)
                d = to_dict(dt)
                components = self.sub_time_components
                return to_nanoseconds(**{key: int(val) for key, val in d.items() if key in components})

            elif self._scope == "hour":
                # ie. 12:30.123
                res = re.search(r"(?P<minute>[0-9][0-9]):(?P<second>[0-9][0-9])([.](?P<microsecond>[0-9]{0,6}))?(?P<nanosecond>[0-9]+)?", value, flags=re.IGNORECASE)
                if res:
                    if res["microsecond"] is not None:
                        res["microsecond"] = res["microsecond"].ljust(6, "0")
                    return to_nanoseconds(**{key: int(val) for key, val in res.groupdict().items() if val is not None})
            elif self._scope == "minute":
                # ie. 30.123
                res = re.search(r"(?P<second>[0-9][0-9])([.](?P<microsecond>[0-9]{0,6}))?(?P<nanosecond>[0-9]+)?", value, flags=re.IGNORECASE)
                if res:
                    res["microsecond"] = res["microsecond"].ljust(6, "0")
                    return to_nanoseconds(**{key: int(val) for key, val in res.groupdict().items() if val is not None})

            # Last try
            if self._scope in ("hour", "minute"):
                # ie. 1 quarter
                res = re.search(r"(?P<n>[1-4] ?(quarter|q))", value, flags=re.IGNORECASE)
                if res:
                    # ie. "1 quarter"
                    n_quarters = res["n"]
                    component = self.sub_time_components[0]
                    return to_nanoseconds(**{component: n_quarters * 15})


        raise TypeError(value)

    @property
    def sub_time_components(self):
        "Sub time components of the interval"
        components = self.components
        return components[components.index(self._scope) + 1:]

    def __repr__(self):
        return f'{self._scope}({self.start}, {self.end})'

class TimeOfSecond(AnchoredInterval):
    # WIP!
    _scope = "second"

class TimeOfMinute(AnchoredInterval):
    # WIP!
    _scope = "minute"

class TimeOfHour(AnchoredInterval):
    # WIP!
    _scope = "hour"

class TimeOfDay(AnchoredInterval):
    # WIP!
    _scope = "day"

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
