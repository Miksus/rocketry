

from datetime import datetime
import re
from typing import Union
import dateutil
import calendar
from abc import abstractmethod

import pandas as pd
from .utils import to_nanoseconds, timedelta_to_str, to_dict
from .base import TimeCycle, TimeInterval


class AnchoredInterval(TimeInterval):
    """Base class for interval for those that have 
    fixed time unit (that can be converted to nanoseconds).

    Converts start and end to nanoseconds where
    0 represents the beginning of the interval
    (ie. for a week: monday 00:00 AM) and max
    is number of nanoseconds from start to the
    end of the interval.
    
    Examples for start=0 nanoseconds
        - for a week: Monday
        - for a day: 00:00
        - for a month: 1st day
    

    Methods:
    --------
        anchor_dict --> int : Calculate corresponding nanoseconds from dict
        anchor_str --> int : Calculate corresponding nanoseconds from string
        anchor_int --> int : Calculate corresponding nanoseconds from integer

    Properties:
        start --> int : Nanoseconds on the interval till the start
        end   --> int : Nanoseconds on the interval till the end 

    Class attributes:
    -----------------
        _scope [str] : 
    """
    components = ("year", "month", "week", "day", "hour", "minute", "second", "microsecond", "nanosecond")

    _fixed_components = ("week", "day", "hour", "minute", "second", "microsecond", "nanosecond")

    _scope = None # ie. day, hour, second, microsecond
    _scope_max = None

    def __init__(self, start=None, end=None):
        self.start = start
        self.end = end

    def anchor(self, value, **kwargs):
        "Turn value to nanoseconds relative to scope of the class"
        if isinstance(value, dict):
            # {"hour": 10, "minute": 20}
            return self.anchor_dict(value, **kwargs)

        elif isinstance(value, int):
            # start is considered as unit of the second behind scope
            return self.anchor_int(value, **kwargs)

        elif isinstance(value, str):
            return self.anchor_str(value, **kwargs)
        raise TypeError(value)

    def anchor_int(self, i, **kwargs):
        return to_nanoseconds(**{self._scope: i})

    def anchor_dict(self, d, **kwargs):
        comps = self._fixed_components[(self._fixed_components.index(self._scope) + 1):]
        kwargs = {key: val for key, val in d.items() if key in comps}
        return to_nanoseconds(**kwargs)

    def anchor_dt(self, dt: Union[datetime, pd.Timestamp], **kwargs) -> int:
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

    @property
    def start(self):
        delta = pd.Timedelta(self._start, unit="ns")
        repr_scope = self.components[self.components.index(self._scope) + 1]
        return timedelta_to_str(delta, default_scope=repr_scope)

    @start.setter
    def start(self, val):
        self._start = (
            self.anchor(val, side="start") 
            if val is not None 
            else 0
        )

    @property
    def end(self):
        delta = pd.Timedelta(self._end, unit="ns")
        repr_scope = self.components[self.components.index(self._scope) + 1]
        return timedelta_to_str(delta, default_scope=repr_scope)

    @end.setter
    def end(self, val):
        ns = (
            self.anchor(val, side="end") 
            if val is not None 
            else self._scope_max
        )

        has_time = (ns % to_nanoseconds(day=1)) != 0

        self._end = ns

    @abstractmethod
    def anchor_str(self, s, **kwargs):
        raise NotImplementedError

    @classmethod
    def from_starting(cls, starting):
        # Replaces TimeCycles
        obj = cls(starting)
        if obj._start != 0:
            # End is one nanosecond away from start
            obj._end = obj._start - 1 

    def __contains__(self, dt) -> bool:
        "Whether dt is in the interval"

        ns_start = self._start
        ns_end = self._end

        if ns_start == ns_end:
            # As there is no time in between, 
            # the interval is considered full
            # cycle (ie. from 10:00 to 10:00)
            return True

        ns = self.anchor_dt(dt) # In relative nanoseconds (removed more accurate than scope)


        is_over_period = ns_start > ns_end # period is overnight, over weekend etc.
        if not is_over_period:
            return ns_start <= ns <= ns_end
        else:
            return ns >= ns_start or ns <= ns_end

    def get_scope_back(self, dt):
        "Override if offsetting back is different than forward"
        return self._scope_max

    def get_scope_forward(self, dt):
        "Override if offsetting back is different than forward"
        return self._scope_max

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
        ns = self.anchor_dt(dt) # In relative nanoseconds (removed more accurate than scope)
        ns_start = self._start
        ns_end = self._end

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
            offset = pd.Timedelta(int(ns_start) - int(ns), unit="ns")
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
            ns_scope = self.get_scope_forward(dt)
            offset = pd.Timedelta(int(ns_start) - int(ns) + ns_scope, unit="ns")
        return dt + offset

    def next_end(self, dt):
        "Get next end point of the period"
        ns = self.anchor_dt(dt) # In relative nanoseconds (removed more accurate than scope)
        ns_start = self._start
        ns_end = self._end

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
            offset = pd.Timedelta(int(ns_end) - int(ns), unit="ns")
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
            ns_scope = self.get_scope_forward(dt)
            offset = pd.Timedelta(int(ns_end) - int(ns) + ns_scope, unit="ns")
        return dt + offset

    def prev_start(self, dt):
        "Get previous start point of the period"
        ns = self.anchor_dt(dt) # In relative nanoseconds (removed more accurate than scope)
        ns_start = self._start
        ns_end = self._end

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
            ns_scope = self.get_scope_back(dt)
            offset = pd.Timedelta(int(ns_start) - int(ns) - ns_scope, unit="ns")
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
            offset = pd.Timedelta(int(ns_start) - int(ns), unit="ns")
        return dt + offset

    def prev_end(self, dt):
        "Get pervious end point of the period"
        ns = self.anchor_dt(dt) # In relative nanoseconds (removed more accurate than scope)
        ns_start = self._start
        ns_end = self._end

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
            ns_scope = self.get_scope_back(dt)
            offset = pd.Timedelta(int(ns_end) - int(ns) - ns_scope, unit="ns")
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
            offset = pd.Timedelta(int(ns_end) - int(ns), unit="ns")

        return dt + offset

    def __repr__(self):
        return f'{self._scope}({self._start}, {self._end})'

    def __str__(self):
        # Hour: '15:'
        start_ns = self._start
        end_ns = self._end

        scope = self._scope
        repr_scope = self.components[self.components.index(self._scope) + 1]

        to_start = pd.Timedelta(start_ns, unit="ns")
        to_end = pd.Timedelta(end_ns, unit="ns")

        start_str = timedelta_to_str(to_start, default_scope=repr_scope)
        end_str = timedelta_to_str(to_end, default_scope=repr_scope)

        start_str = f"0 {repr_scope}s" if not start_str else start_str
        return f"{start_str} - {end_str}"

class MinuteMixin:

    _scope = "minute"
    _scope_max = to_nanoseconds(minute=1) # See: pd.Timedelta(59999999999, unit="ns")

    def anchor_str(self, s):
        # ie. 30.123
        res = re.search(r"(?P<second>[0-9][0-9])([.](?P<microsecond>[0-9]{0,6}))?(?P<nanosecond>[0-9]+)?", value, flags=re.IGNORECASE)
        if res:
            res["microsecond"] = res["microsecond"].ljust(6, "0")
            return to_nanoseconds(**{key: int(val) for key, val in res.groupdict().items() if val is not None})

        res = re.search(r"(?P<n>[1-4] ?(quarter|q))", value, flags=re.IGNORECASE)
        if res:
            # ie. "1 quarter"
            n_quarters = res["n"]
            return self._scope_max / 4 * n_quarters

class HourMixin:

    _scope = "hour"
    _scope_max = to_nanoseconds(hour=1)

    def anchor_str(self, s):
        # ie. 12:30.123
        res = re.search(r"(?P<minute>[0-9][0-9]):(?P<second>[0-9][0-9])([.](?P<microsecond>[0-9]{0,6}))?(?P<nanosecond>[0-9]+)?", s, flags=re.IGNORECASE)
        if res:
            if res["microsecond"] is not None:
                res["microsecond"] = res["microsecond"].ljust(6, "0")
            return to_nanoseconds(**{key: int(val) for key, val in res.groupdict().items() if val is not None})

        res = re.search(r"(?P<n>[1-4] ?(quarter|q))", value, flags=re.IGNORECASE)
        if res:
            # ie. "1 quarter"
            n_quarters = res["n"]
            return self._scope_max / 4 * n_quarters

class DayMixin:

    _scope = "day"
    _scope_max = to_nanoseconds(day=1)
    
    def anchor_str(self, s):
        # ie. "10:00:15"
        dt = dateutil.parser.parse(s)
        d = to_dict(dt)
        components = ("hour", "minute", "second", "microsecond", "nanosecond")
        return to_nanoseconds(**{key: int(val) for key, val in d.items() if key in components})

    def anchor_dt(self, dt):
        "Turn datetime to nanoseconds according to the scope (by removing higher time elements)"
        d = to_dict(dt)
        d = {
            key: val
            for key, val in d.items()
            if key in ("hour", "minute", "second", "microsecond", "nanosecond")
        }
        return to_nanoseconds(**d) 

class WeekMixin:

    _scope = "week"
    _scope_max = to_nanoseconds(day=1) * 7

    weeknum_mapping = {
        **dict(zip(calendar.day_name, range(7))), 
        **dict(zip(calendar.day_abbr, range(7))), 
        **dict(zip(range(7), range(7)))
    }
    # TODO: ceil end
    def anchor_str(self, s):
        # Allowed:
        #   "Mon", "Monday", "Mon 10:00:00"
        res = re.search(r"(?P<dayofweek>[a-z]+) ?(?P<time>.*)", s, flags=re.IGNORECASE)
        comps = res.groupdict()
        dayofweek = comps.pop("dayofweek")
        time = comps.pop("time")
        nth_day = self.weeknum_mapping[dayofweek]

        # TODO: TimeOfDay.anchor_str as function
        nanoseconds = DayMixin().anchor_str(time) if time else 0

        return DayMixin._scope_max * nth_day + nanoseconds

    def anchor_dt(self, dt):
        "Turn datetime to nanoseconds according to the scope (by removing higher time elements)"
        d = to_dict(dt)
        d = {
            key: val
            for key, val in d.items()
            if key in ("hour", "minute", "second", "microsecond", "nanosecond")
        }
        dayofweek = dt.weekday()
        return to_nanoseconds(**d) + dayofweek * 8.64e+13

class MonthMixin:

    _scope = "year"
     # NOTE: Floating
    # TODO: ceil end and implement reversion (last 5th day)

    def anchor_str(self, s):
        # Allowed:
        #   "5th", "1st", "5", "3rd 12:30:00"
        #   TODO: "first 5th", "last 5th", "last 3rd 10:00:00"
        res = re.search(r"(?P<dayofmonth>[0-9]+)(st|nd|rd|th)? ?(?P<time>.*)", s, flags=re.IGNORECASE)
        comps = res.groupdict()
        dayofmonth = comps.pop("dayofmonth")
        time = comps.pop("time")
        nth_day = int(dayofmonth)

        # TODO: TimeOfDay.anchor_str as function
        nanoseconds = DayMixin().anchor_str(time) if time else 0

        return DayMixin._scope_max * nth_day + nanoseconds

    def anchor_dt(self, dt):
        "Turn datetime to nanoseconds according to the scope (by removing higher time elements)"
        d = to_dict(dt)
        d = {
            key: val
            for key, val in d.items()
            if key in ("day", "hour", "minute", "second", "microsecond", "nanosecond")
        }

        return to_nanoseconds(**d)

    def get_scope_forward(self, dt):
        n_days = calendar.monthrange(dt.year, dt.month)[1]
        return to_nanoseconds(day=1) * n_days

    def get_scope_back(self, dt):
        month = 12 if dt.month == 1 else dt.month - 1
        year = dt.year - 1 if dt.month == 1 else dt.year
        n_days = calendar.monthrange(year, month)[1]
        return to_nanoseconds(day=1) * n_days

class YearMixin:

    _scope = "year"
    _scope_max = to_nanoseconds(day=1) * 366

    monthnum_mapping = {
        **dict(zip(calendar.month_name[1:], range(12))), 
        **dict(zip(calendar.month_abbr[1:], range(12))), 
        **dict(zip(range(12), range(12)))
    }
    # NOTE: Floating

    def anchor_str(self, s):
        # Allowed:
        #   "January", "Dec", "12", "Dec last 5th 10:00:00"
        res = re.search(r"(?P<monthofyear>[a-z]+) ?(?P<month>.*)", s, flags=re.IGNORECASE)
        comps = res.groupdict()
        monthofyear = comps.pop("monthofyear")
        month_str = comps.pop("month")
        nth_month = self.monthnum_mapping[monthofyear]

        # TODO: TimeOfDay.anchor_str as function
        nanoseconds = MonthMixin().anchor_str(month_str) if month_str else 0

        return MonthMixin._scope_max * (nth_month * TimeOfMonth.days_in_month) + nanoseconds

    def anchor_dt(self, dt):
        "Turn datetime to nanoseconds according to the scope (by removing higher time elements)"
        days_in_month = 31
        d = to_dict(dt)
        d = {
            key: val
            for key, val in d.items()
            if key in ("day", "hour", "minute", "second", "microsecond", "nanosecond")
        }

        return to_nanoseconds(**d) + d["month"] * 8.64e+13 * days_in_month