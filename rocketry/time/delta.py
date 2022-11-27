import time
import datetime
from dataclasses import dataclass, field
from typing import Callable, Union

from rocketry.core.time import TimeDelta
from rocketry.pybox.time import to_timedelta, Interval

@dataclass(frozen=True, init=False)
class TimeSpanDelta(TimeDelta):

    near: int
    far: int
    reference: Union[datetime.datetime, Callable] = field(default=None)

    def __init__(self, near=None, far=None, reference=None, **kwargs):

        near = 0 if near is None else near
        object.__setattr__(self, "near", abs(to_timedelta(near, **kwargs)))
        object.__setattr__(self, "far", abs(to_timedelta(far, **kwargs)) if far is not None else None)
        object.__setattr__(self, "reference", reference)

    def use_reference(self, ref):
        return TimeSpanDelta(near=self.near, far=self.far, reference=ref)

    def __contains__(self, dt):
        "Check whether the dt is period"
        reference = self.get_reference()
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
        is_same_class = isinstance(self, type(other))
        if is_same_class:
            return (self.near == other.near) and (self.far == other.far)
        return False

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"TimeSpanDelta(near={repr(self.near)}, far={repr(self.far)})"
