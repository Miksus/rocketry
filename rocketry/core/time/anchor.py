from datetime import datetime
from typing import ClassVar, Dict, List, Tuple, Union
from abc import abstractmethod
from dataclasses import dataclass

from rocketry.pybox.time import to_microseconds, timedelta_to_str, datetime_to_dict, to_timedelta
from .base import Any, TimeInterval

@dataclass(frozen=True, repr=False)
class AnchoredInterval(TimeInterval):
    """Base class for interval for those that have
    fixed time unit (that can be converted to microseconds).

    Converts start and end to microseconds where
    0 represents the beginning of the interval
    (ie. for a week: monday 00:00 AM) and max
    is number of microseconds from start to the
    end of the interval.

    Examples for start=0 microseconds
        - for a week: Monday
        - for a day: 00:00
        - for a month: 1st day


    Methods:
    --------
        anchor_dict --> int : Calculate corresponding microseconds from dict
        anchor_str --> int : Calculate corresponding microseconds from string
        anchor_int --> int : Calculate corresponding microseconds from integer

    Properties:
        start --> int : microseconds on the interval till the start
        end   --> int : microseconds on the interval till the end

    Class attributes:
    -----------------
        _scope [str] :
    """
    _start: int
    _end: int

    components: ClassVar[Tuple[str]] = ("year", "month", "week", "day", "hour", "minute", "second", "microsecond")

    # Components that have always fixed length (exactly the same amount of time)
    _fixed_components: ClassVar[Tuple[str]] = ("week", "day", "hour", "minute", "second", "microsecond")

    _scope: ClassVar[str] = None # Scope of the full period. Ie. day, hour, second, microsecond
    _scope_max: ClassVar[int] = None # Max in microseconds of the

    _unit_resolution: ClassVar[int] = None # Microseconds of one unit (if start/end is int)
    _unit_names: ClassVar[List] = None
    _unit_mapping: ClassVar[Dict[str, int]] = {}

    def __init__(self, start=None, end=None, time_point=None, starting=None, right_closed=False):

        if start is None and end is None:
            if time_point:
                raise ValueError("Full cycle cannot be point of time")
            object.__setattr__(self, "_start", 0)
            object.__setattr__(self, "_end", self._scope_max)
        else:
            self.set_start(start)
            self.set_end(end, time_point=time_point, right_closed=right_closed, starting=starting)

    def anchor(self, value, **kwargs):
        "Turn value to nanoseconds relative to scope of the class"
        if isinstance(value, dict):
            # {"hour": 10, "minute": 20}
            return self.anchor_dict(value, **kwargs)

        if isinstance(value, int):
            # start is considered as unit of the second behind scope
            return self.anchor_int(value, **kwargs)

        if isinstance(value, float):
            # start is considered as unit of the second behind scope
            return self.anchor_float(value, **kwargs)

        if isinstance(value, str):
            return self.anchor_str(value, **kwargs)
        raise TypeError(value)

    def anchor_float(self, i, **kwargs):
        raise ValueError("Float conversion not supported")

    def anchor_int(self, i, side=None, time_point=None, **kwargs):
        if side == "end":
            return (i + 1) * self._unit_resolution
        return i * self._unit_resolution

    def anchor_dict(self, d, **kwargs):
        comps = self._fixed_components[(self._fixed_components.index(self._scope) + 1):]
        kwargs = {key: val for key, val in d.items() if key in comps}
        return to_microseconds(**kwargs)

    def anchor_dt(self, dt: datetime, **kwargs) -> int:
        "Turn datetime to nanoseconds according to the scope (by removing higher time elements)"
        components = self.components
        components = components[components.index(self._scope) + 1:]
        d = datetime_to_dict(dt)
        d = {
            key: val
            for key, val in d.items()
            if key in components
        }

        return to_microseconds(**d)

    @classmethod
    def create_range(cls, start:Union[str, int]=None, end:Union[str, int]=None, step:int=None):
        if isinstance(start, str):
            start = cls._unit_mapping[start.lower()]
        if isinstance(end, str):
            end = cls._unit_mapping[end.lower()]

        periods = tuple(
            cls.at(step)
            for step in cls._unit_names[start:end:step]
        )
        return Any(*periods)

    def set_start(self, val):
        if val is None:
            ms = 0
        else:
            ms = self.anchor(val, side="start")
        self._validate(ms, orig=val)
        object.__setattr__(self, "_start", ms)
        object.__setattr__(self, "_start_orig", val)

    def set_end(self, val, right_closed=False, time_point=False, starting=False):
        if time_point and val is None:
            # Interval is "at" type, ie. on monday, at 10:00 (10:00 - 10:59:59)
            ms = self.to_timepoint(self._start)
        elif starting and val is None:
            ms = self._start
        elif val is None:
            ms = self._scope_max
        else:
            ms = self.anchor(val, side="end", time_point=time_point)

        if right_closed:
            # We use left closed in intervals so we add one unit to make it closed
            # given the end argument, ie. if "09:00 to 10:00" excludes 10:00
            # we can include it by adding one nanosecond to 10:00
            ms += 1
        self._validate(ms, orig=val)
        object.__setattr__(self, "_end", ms)
        object.__setattr__(self, "_end_orig", val)

    def to_timepoint(self, ms:int):
        "Turn microseconds to the period's timepoint"
        # Ie. Monday --> Monday 00:00 to Monday 24:00
        # By default assumes linear scale (like week)
        # but can be overridden for non linear such as year
        end_ms = ms + self._unit_resolution
        if end_ms >= self._scope_max:
            # Over period
            end_ms -= self._scope_max
        return end_ms

    def _validate(self, n:int, orig):
        if n < 0 or n > self._scope_max:
            raise ValueError(f"Out of bound: {repr(orig)}")

    @property
    def start(self):
        delta = to_timedelta(self._start, unit="microsecond")
        repr_scope = self.components[self.components.index(self._scope) + 1]
        return timedelta_to_str(delta, default_scope=repr_scope)

    @start.setter
    def start(self, val):
        self.set_start(val)

    @property
    def end(self):
        delta = to_timedelta(self._end, unit="microsecond")
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

        ms_start = self._start
        ms_end = self._end

        if self.is_full():
            # As there is no time in between,
            # the interval is considered full
            # cycle (ie. from 10:00 to 10:00)
            return True

        ms = self.anchor_dt(dt) # In relative nanoseconds (removed more accurate than scope)

        is_over_period = ms_start > ms_end # period is overnight, over weekend etc.
        if not is_over_period:
            # Note that the period is right opened (end point excluded)
            return ms_start <= ms < ms_end
        # Note that the period is right opened (end point excluded)
        return ms >= ms_start or ms < ms_end

    def is_full(self):
        "Whether every time belongs to the period (but there is still distinct intervals)"
        return (self._start == self._end) or (self._start == 0 and self._end == self._scope_max)

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
        return self.next_start(dt)

    def rollend(self, dt):
        "Roll back to previous point in time that is on the period"
        if dt in self:
            return dt
        return self.prev_end(dt)

    def next_start(self, dt):
        "Get next start point of the period"
        ms = self.anchor_dt(dt) # In relative nanoseconds (removed more accurate than scope)
        ms_start = self._start
        ms_end = self._end

        if ms < ms_start:
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
            offset = to_timedelta(int(ms_start) - int(ms), unit="microsecond")
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
            ms_scope = self.get_scope_forward(dt)
            offset = to_timedelta(int(ms_start) - int(ms) + ms_scope, unit="microsecond")
        return dt + offset

    def next_end(self, dt):
        "Get next end point of the period"
        ms = self.anchor_dt(dt) # In relative nanoseconds (removed more accurate than scope)
        ms_start = self._start
        ms_end = self._end

        if ms < ms_end:
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
            offset = to_timedelta(int(ms_end) - int(ms), unit="microsecond")
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
            ms_scope = self.get_scope_forward(dt)
            offset = to_timedelta(int(ms_end) - int(ms) + ms_scope, unit="microsecond")
        return dt + offset

    def prev_start(self, dt):
        "Get previous start point of the period"
        ms = self.anchor_dt(dt) # In relative nanoseconds (removed more accurate than scope)
        ms_start = self._start

        if ms < ms_start:
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
            ms_scope = self.get_scope_back(dt)
            offset = to_timedelta(int(ms_start) - int(ms) - ms_scope, unit="microsecond")
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
            offset = to_timedelta(int(ms_start) - int(ms), unit="microsecond")
        return dt + offset

    def prev_end(self, dt):
        "Get pervious end point of the period"
        ms = self.anchor_dt(dt) # In relative nanoseconds (removed more accurate than scope)
        ms_end = self._end

        if ms < ms_end:
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
            ms_scope = self.get_scope_back(dt)
            offset = to_timedelta(int(ms_end) - int(ms) - ms_scope, unit="microsecond")
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
            offset = to_timedelta(int(ms_end) - int(ms), unit="microsecond")

        return dt + offset

    def repr_ms(self, n:int):
        "Microseconds to representative format"
        return repr(n)

    def __repr__(self):
        cls_name = type(self).__name__
        start = self.repr_ms(self._start) if not hasattr(self, "_start_orgi") else self._start_orig
        end = self.repr_ms(self._end) if not hasattr(self, "_end_orgi") else self._end_orig
        return f'{cls_name}({start}, {end})'

    def __str__(self):
        # Hour: '15:'
        start_ms = self._start
        end_ms = self._end

        repr_scope = self.components[self.components.index(self._scope) + 1]

        to_start = to_timedelta(start_ms, unit="microsecond")
        to_end = to_timedelta(end_ms, unit="microsecond")

        start_str = timedelta_to_str(to_start, default_scope=repr_scope)
        end_str = timedelta_to_str(to_end, default_scope=repr_scope)

        start_str = f"0 {repr_scope}s" if not start_str else start_str
        return f"{start_str} - {end_str}"

    @classmethod
    def at(cls, value):
        return cls(value, time_point=True)

    @classmethod
    def starting(cls, value):
        return cls(value, starting=True)
