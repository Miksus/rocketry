

import re
import dateutil
import calendar

import pandas as pd
from .utils import to_nanoseconds, timedelta_to_str, to_dict
from .base import TimeCycle, TimeInterval

class AnchoredMixin:

    _fixed_components = ("year", "month", "day", "hour", "minute", "second", "microsecond", "nanosecond")

    _scope = None # ie. day, hour, second, microsecond
    _scope_max = None

    def anchor_int(self, i):
        return to_nanoseconds(**{self._scope: i})

    def anchor_dict(self, d):
        comps = self._fixed_components[(self._fixed_components.index(self._scope) + 1):]
        kwargs = {key: val for key, val in d.items() if key in comps}
        return to_nanoseconds(**kwargs)

    def anchor(self, value):
        "Turn value to nanoseconds relative to scope of the class"
        if isinstance(value, dict):
            # {"hour": 10, "minute": 20}
            return self.anchor_dict(value)

        elif isinstance(value, int):
            # start is considered as unit of the second behind scope
            return self.anchor_int(value)

        elif isinstance(value, str):
            return self.anchor_str(value)
        raise TypeError(value)

class AnchoredCycle(AnchoredMixin, TimeCycle):
    
    def __init__(self, start=None):
        self.start = start

    @property
    def start(self):
        delta = pd.Timedelta(self._start, unit="ns")
        return timedelta_to_str(delta)

    @start.setter
    def start(self, val):
        self._start = (
            self.anchor(val) 
            if val is not None 
            else 0
        )
# TODO
    def rollback(self, dt):

        ns = self.anchor_dt(dt)
        ns_offset = self._start - ns
        if ns >= self._start:
            #       dt
            #  -->--------------------->-----------
            #  time   |              time     |    
            pass
        else:
            #               dt
            #  -->--------------------->-----------
            #  time   |              time     |    
            ns_offset -= self._scope_max

        ns_offset = self._start - ns
        offset = pd.Timedelta(ns_offset, unit="ns")

        start = pd.Timestamp(dt) + offset
        end = pd.Timestamp(dt)

        return pd.Interval(start, end)

    def rollforward(self, dt):
        ns = self.anchor_dt(dt)
        ns_offset = self._start - ns

        if ns >= self._start:
            #       dt           (dt_end)
            #  -->--------------------->-----------
            #  time   |              time     |    
            ns_offset += self._scope_max
        else:
            #               dt
            #  -->--------------------->-----------
            #  time   |              time     |    
            pass

        
        offset = pd.Timedelta(ns_offset - 1, unit="ns")

        start = pd.Timestamp(dt)
        end = pd.Timestamp(dt) + offset
        
        return pd.Interval(start, end)

class AnchoredInterval(AnchoredMixin, TimeInterval):
    """Base for interval for those that have fixed time unit (that can be converted to nanoseconds)
    """
    components = ("year", "month", "day", "hour", "minute", "second", "microsecond", "nanosecond")


    _ceil_end_time = False

    def __init__(self, start=None, end=None):
        self.start = start
        self.end = end

    @classmethod
    def from_starting(cls, starting):
        # Replaces TimeCycles
        obj = cls(starting)
        if obj._start != 0:
            # End is one nanosecond away from start
            obj._end = obj._start - 1 

    @property
    def start(self):
        delta = pd.Timedelta(self._start, unit="ns")
        return timedelta_to_str(delta)

    @start.setter
    def start(self, val):
        self._start = (
            self.anchor(val) 
            if val is not None 
            else 0
        )

    @property
    def end(self):
        delta = pd.Timedelta(self._end, unit="ns")
        return timedelta_to_str(delta)

    @end.setter
    def end(self, val):
        ns = (
            self.anchor(val) 
            if val is not None 
            else self._scope_max
        )

        has_time = (ns % to_nanoseconds(day=1)) != 0
        if self._ceil_end_time and has_time:
            ns = ns + (to_nanoseconds(day=1) - 1)

        self._end = ns

    def anchor_dt(self, dt):
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
        "Whether dt is in the interval"

        ns_start = self._start
        ns_end = self._end

        if ns_start == ns_end:
            # As there is no time in between, 
            # the interval is considered full
            # cycle (ie. from 10:00 to 10:00)
            return True

        ns = self.anchor_dt(dt) # In relative nanoseconds (removed more accurate than scope)


        is_over_period = ns_start > ns_end
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
        return f'{self._scope}({self.start}, {self.end})'


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
    _ceil_end_time = True

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
    _ceil_end_time = True
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
    _ceil_end_time = True

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