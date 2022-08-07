

from datetime import datetime
from typing import Union
from abc import abstractmethod

from .utils import to_nanoseconds, timedelta_to_str, to_dict, to_timedelta
from .base import TimeInterval


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

    # Components that have always fixed length (exactly the same amount of time)
    _fixed_components = ("week", "day", "hour", "minute", "second", "microsecond", "nanosecond")

    _scope:str = None # Scope of the full period. Ie. day, hour, second, microsecond
    _scope_max:int = None # Max in nanoseconds of the 

    _unit_resolution: int = None # Nanoseconds of one unit (if start/end is int)

    def __init__(self, start=None, end=None, time_point=None):

        if start is None and end is None:
            if time_point:
                raise ValueError("Full cycle cannot be point of time")
            self._start = 0
            self._end = 0
        else:
            self.set_start(start)
            self.set_end(end, time_point=time_point)

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

    def anchor_int(self, i, side=None, time_point=None, **kwargs):
        if side == "end":
            return (i + 1) * self._unit_resolution - 1
        return i * self._unit_resolution

    def anchor_dict(self, d, **kwargs):
        comps = self._fixed_components[(self._fixed_components.index(self._scope) + 1):]
        kwargs = {key: val for key, val in d.items() if key in comps}
        return to_nanoseconds(**kwargs)

    def anchor_dt(self, dt: datetime, **kwargs) -> int:
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

    def set_start(self, val):
        if val is None:
            ns = 0
        else:
            ns = self.anchor(val, side="start")
        self._start = ns
        self._start_orig = val

    def set_end(self, val, time_point=False):
        if time_point and val is None:
            # Interval is "at" type, ie. on monday, at 10:00 (10:00 - 10:59:59)
            ns = self.to_timepoint(self._start)
        elif val is None:
            ns = self._scope_max            
        else:
            ns = self.anchor(val, side="end", time_point=time_point)

        self._end = ns
        self._end_orig = val

    def to_timepoint(self, ns:int):
        "Turn nanoseconds to the period's timepoint"
        # Ie. Monday --> Monday 00:00 to Monday 24:00
        # By default assumes linear scale (like week)
        # but can be overridden for non linear such as year
        return ns + self._unit_resolution - 1

    @property
    def start(self):
        delta = to_timedelta(self._start, unit="ns")
        repr_scope = self.components[self.components.index(self._scope) + 1]
        return timedelta_to_str(delta, default_scope=repr_scope)

    @start.setter
    def start(self, val):
        self.set_start(val)

    @property
    def end(self):
        delta = to_timedelta(self._end, unit="ns")
        repr_scope = self.components[self.components.index(self._scope) + 1]
        return timedelta_to_str(delta, default_scope=repr_scope)

    @end.setter
    def end(self, val):
        self.set_end(val)

    @abstractmethod
    def anchor_str(self, s, **kwargs) -> int:
        raise NotImplementedError

    def __contains__(self, dt) -> bool:
        "Whether dt is in the interval"

        ns_start = self._start
        ns_end = self._end

        if self.is_full():
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

    def is_full(self):
        "Whether every time belongs to the period (but there is still distinct intervals)"
        return self._start == self._end

    def get_scope_back(self, dt):
        "Override if offsetting back is different than forward"
        return self._scope_max + 1

    def get_scope_forward(self, dt):
        "Override if offsetting back is different than forward"
        return self._scope_max + 1

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
            offset = to_timedelta(int(ns_start) - int(ns), unit="ns")
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
            offset = to_timedelta(int(ns_start) - int(ns) + ns_scope, unit="ns")
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
            offset = to_timedelta(int(ns_end) - int(ns), unit="ns")
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
            offset = to_timedelta(int(ns_end) - int(ns) + ns_scope, unit="ns")
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
            offset = to_timedelta(int(ns_start) - int(ns) - ns_scope, unit="ns")
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
            offset = to_timedelta(int(ns_start) - int(ns), unit="ns")
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
            offset = to_timedelta(int(ns_end) - int(ns) - ns_scope, unit="ns")
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
            offset = to_timedelta(int(ns_end) - int(ns), unit="ns")

        return dt + offset

    def repr_ns(self, n:int):
        "Nanoseconds to representative format"
        return repr(n)

    def __repr__(self):
        cls_name = type(self).__name__
        start = self.repr_ns(self._start) if not hasattr(self, "_start_orgi") else self._start_orig
        end = self.repr_ns(self._end) if not hasattr(self, "_end_orgi") else self._end_orig
        return f'{cls_name}({start}, {end})'

    def __str__(self):
        # Hour: '15:'
        start_ns = self._start
        end_ns = self._end

        scope = self._scope
        repr_scope = self.components[self.components.index(self._scope) + 1]

        to_start = to_timedelta(start_ns, unit="ns")
        to_end = to_timedelta(end_ns, unit="ns")

        start_str = timedelta_to_str(to_start, default_scope=repr_scope)
        end_str = timedelta_to_str(to_end, default_scope=repr_scope)

        start_str = f"0 {repr_scope}s" if not start_str else start_str
        return f"{start_str} - {end_str}"

    @classmethod
    def at(cls, value):
        return cls(value, time_point=True)

    @classmethod
    def starting(cls, value):
        return cls(value, value)