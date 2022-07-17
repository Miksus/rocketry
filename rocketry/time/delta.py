import time
import datetime

from rocketry.core.time import TimeDelta
from rocketry.pybox.time import to_datetime, to_timedelta, Interval

class TimeSpanDelta(TimeDelta):

    def __init__(self, near=None, far=None, **kwargs):

        near = 0 if near is None else near        
        self.near = abs(to_timedelta(near, **kwargs))
        self.far = abs(to_timedelta(far, **kwargs)) if far is not None else None


    def __contains__(self, dt):
        "Check whether the datetime is in "
        reference = getattr(self, "reference", datetime.datetime.fromtimestamp(time.time()))
        if reference >= dt:
            start = reference - self.far if self.far is not None else self.min
            end = reference - self.near
        else:
            start = reference + self.near
            end = reference + self.far if self.far is not None else self.max
        return start <= dt <= end

    def rollback(self, dt):
        "Get previous interval (including currently ongoing)"
        start = dt - self.far if self.far is not None else self.min 
        end = dt - self.near
        return Interval(start, end) 

    def rollforward(self, dt):
        "Get next interval (including currently ongoing)"
        start = dt + self.near
        end = dt + self.far if self.far is not None else self.max
        return Interval(start, end) 

    def __eq__(self, other):
        "Test whether self and other are essentially the same periods"
        is_same_class = type(self) == type(other)
        if is_same_class:
            return (self.near == other.near) and (self.far == other.far)
        else:
            return False

    def __repr__(self):
        return f"TimeSpanDelta(start={repr(self.start)}, end={repr(self.end)})"