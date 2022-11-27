import datetime
from functools import reduce
import time
from abc import abstractmethod
from typing import Callable, ClassVar, Dict, FrozenSet, List, Optional, Pattern, Union
import itertools
from dataclasses import dataclass, field

from rocketry._base import RedBase
from rocketry.pybox.time import to_datetime, to_timedelta, Interval

PARSERS: Dict[Union[str, Pattern], Union[Callable, 'TimePeriod']] = {}

@dataclass(frozen=True)
class TimePeriod(RedBase):
    """Base for all classes that represent a time period.

    Time period is a period in time with a start and an end.
    These are useful to determine whether an event took
    place in a specific time span or whether current time
    is in a given time span.
    """

    resolution: ClassVar[datetime.timedelta] = datetime.timedelta.resolution
    min: ClassVar[datetime.datetime] = datetime.datetime(1970, 1, 3, 2, 0)
    max: ClassVar[datetime.datetime] = datetime.datetime(2260, 1, 1, 0, 0)

    def __contains__(self, other):
        """Whether a given point of time is in
        the TimePeriod"""
        interval = self.rollforward(other)
        return other in interval

    def __and__(self, other):
        # self & other
        # bitwise and
        # using & operator
        is_time_period = isinstance(other, TimePeriod)
        if not is_time_period:
            raise TypeError(f"AND operator only supports TimePeriod. Given: {type(other)}")

        if self is always:
            # Reducing the operation
            return other
        if other is always:
            # Reducing the operation
            return self
        return All(self, other)

    def __or__(self, other):
        # self | other
        # bitwise or
        is_time_period = isinstance(other, TimePeriod)
        if not is_time_period:
            raise TypeError(f"AND operator only supports TimePeriod. Given: {type(other)}")

        if self is always or other is always:
            # Reducing the operation
            return always
        return Any(self, other)

    @abstractmethod
    def rollforward(self, dt):
        "Get previous time interval of the period."
        raise NotImplementedError

    @abstractmethod
    def rollback(self, dt):
        "Get previous time interval of the period."
        raise NotImplementedError

class TimeInterval(TimePeriod):
    """Base for all time intervals

    Time interval is a period between two fixed but repeating
    times. Fixed repeated times are defined as time elements
    that repeats constantly but are fixed in a sense that
    if the datetime of an event is known, the question
    whether the event belongs to the period can be answered
    unambigiously.

    Answers to "between 11:00 and 12:00" and "from monday to tuesday"
    """
    _type_name: ClassVar = "interval"
    @abstractmethod
    def __contains__(self, dt):
        "Check whether the datetime is on the period"
        raise NotImplementedError("Contains not implemented.")

    @abstractmethod
    def rollstart(self, dt):
        "Roll forward to next point in time that on the period"
        raise NotImplementedError("Contains not implemented.")

    @abstractmethod
    def rollend(self, dt):
        "Roll back to previous point in time that is on the period"
        raise NotImplementedError("Contains not implemented.")

    @abstractmethod
    def next_start(self, dt):
        "Get next start point of the period"
        raise NotImplementedError("Contains not implemented.")

    @abstractmethod
    def next_end(self, dt):
        "Get next end point of the period"
        raise NotImplementedError("Contains not implemented.")

    @abstractmethod
    def prev_start(self, dt):
        "Get previous start point of the period"
        raise NotImplementedError("Contains not implemented.")

    @abstractmethod
    def prev_end(self, dt):
        "Get pervious end point of the period"
        raise NotImplementedError("Contains not implemented.")

    @abstractmethod
    def from_between(start, end) -> Interval:
        raise NotImplementedError("__between__ not implemented.")

    def is_full(self):
        "Whether every time belongs to the period (but there is still distinct intervals)"
        return False

    def rollforward(self, dt) -> datetime.datetime:
        "Get next time interval of the period"

        closed = "left"
        if self.is_full():
            # Full period so dt always belongs on it
            start = dt
            end = self.next_end(dt)
            if end == start:
                # Expanding the interval
                end = self.next_end(dt + self.resolution)
        else:
            start = self.rollstart(dt)
            end = self.next_end(dt)
            if start == end:
                # The interval is left closed so this should
                # not contain any points. We look for another
                # one
                return self.rollforward(end + self.resolution)

        start = to_datetime(start)
        end = to_datetime(end)

        return Interval(start, end, closed=closed)

    def rollback(self, dt) -> Interval:
        "Get previous time interval of the period"

        closed = "left"
        if self.is_full():
            # Full period so dt always belongs on it
            end = dt
            start = self.prev_start(dt)
            if end == start:
                # Expanding the interval
                start = self.prev_start(dt - self.resolution)
        else:
            end = self.rollend(dt)
            start = self.prev_start(dt)
            if start == end:
                # The interval is left closed but the start
                # is included in the interval. Therefore
                # we include a single point (both sides closed)
                closed = "both"

        start = to_datetime(start)
        end = to_datetime(end)

        return Interval(start, end, closed=closed)

    def __eq__(self, other):
        "Test whether self and other are essentially the same periods"
        is_same_class = isinstance(self, type(other))
        if is_same_class:
            return (self._start == other._start) and (self._end == other._end)
        return False

@dataclass(frozen=True)
class TimeDelta(TimePeriod):
    """Base for all time deltas

    Time delta is a period of time from a reference
    point. It is floating in nature as it could
    contain arbitrary datetimes depending on where
    the reference point is set. This reference
    point is typically current datetime.
    """
    _type_name: ClassVar = "delta"

    reference: Optional[datetime.datetime] = field(default=None)

    def __init__(self, past=None, future=None, reference=None, *, kws_past=None, kws_future=None):

        past = 0 if past is None else past
        future = 0 if future is None else future

        kws_past = {} if kws_past is None else kws_past
        kws_future = {} if kws_future is None else kws_future

        object.__setattr__(self, "past", abs(to_timedelta(past, **kws_past)))
        object.__setattr__(self, "future", abs(to_timedelta(future, **kws_future)))
        object.__setattr__(self, "reference", reference)

    def use_reference(self, ref):
        return TimeDelta(past=self.past, future=self.future, reference=ref)

    @abstractmethod
    def __contains__(self, dt):
        "Check whether the datetime is in "
        reference = self.get_reference()
        start = reference - abs(self.past)
        end = reference + abs(self.future)
        return start <= dt <= end

    def get_reference(self) -> datetime.datetime:
        return self.reference

    def rollback(self, dt):
        "Get previous interval (including currently ongoing)"
        start = dt - abs(self.past)
        start = to_datetime(start)
        end = to_datetime(dt)
        return Interval(start, end)

    def rollforward(self, dt):
        "Get next interval (including currently ongoing)"
        end = dt + abs(self.future)
        start = to_datetime(dt)
        end = to_datetime(end)
        return Interval(start, end)

    def __eq__(self, other):
        "Test whether self and other are essentially the same periods"
        is_same_class = isinstance(self, type(other))
        if is_same_class:
            return (self.past == other.past) and (self.future == other.future)
        return False

    def __str__(self):
        if not self.future:
            return f"past {str(self.past)}"
        if not self.past:
            return f"next {str(self.future)}"
        return f"past {str(self.past)} to next {str(self.future)}"

    def __repr__(self):
        return f"TimeDelta(past={repr(self.past)}, future={repr(self.future)})"

def all_overlap(times:List[Interval]):
    return all(a.overlaps(b) for a, b in itertools.combinations(times, 2))

def get_overlapping(times):
    # Example:
    # A:    <-------------->
    # B:     <------>
    # C:         <------>
    # Out:       <-->
    starts = [interval.left for interval in times]
    ends = [interval.right for interval in times]

    start = max(starts)
    end = min(ends)
    return Interval(start, end)

@dataclass(frozen=True)
class All(TimePeriod):

    periods: FrozenSet[TimePeriod]

    def __init__(self, *args):
        if any(not isinstance(arg, TimePeriod) for arg in args):
            raise TypeError("Only TimePeriods supported")
        if not args:
            raise ValueError("No TimePeriods to wrap")

        # Compress the time periods
        periods = []
        for arg in args:
            if isinstance(arg, All):
                # Don't nest unnecessarily
                periods += list(arg.periods)
            elif arg is always:
                # Does not really have an effect
                continue
            else:
                periods.append(arg)

        object.__setattr__(self, "periods", frozenset(periods))

    def rollback(self, dt):

        # We solve this iteratively
        # 1. rollback
        # 2. check if everything overlaps
        # 3. If not overlaps, take max and check again
        # 4. If overlaps, get the period that overlaps

        intervals = [
            period.rollback(dt)
            for period in self.periods
        ]
        all_overlaps = all(a.overlaps(b) for a, b in itertools.combinations(intervals, 2))
        if all_overlaps:
            return reduce(lambda a, b: a & b, intervals)
        # Not found, trying again with next period
        # Example:
        # Current:                     |
        # A:         <-------------->
        # B:         <---> <--->
        # C:         <------>
        # Next try:         |
        next_dt = min(intervals, key=lambda x: x.right).right

        opened = any(
            interv.closed not in ('right', 'both')
            for interv in intervals
            if interv.right == next_dt
        )
        # TODO: If
        if dt == next_dt:
            next_dt -= self.resolution
        return self.rollback(next_dt)

    def rollforward(self, dt):
        # We solve this iteratively
        # 1. rollforward
        # 2. check if everything overlaps
        # 3. If not overlaps, take max and check again
        # 4. If overlaps, get the period that overlaps

        intervals = [
            period.rollforward(dt)
            for period in self.periods
        ]
        all_overlaps = all(a.overlaps(b) for a, b in itertools.combinations(intervals, 2))
        if all_overlaps:
            return reduce(lambda a, b: a & b, intervals)
        # Not found, trying again with next period
        # Example:
        # Current: |
        # A:         <-------------->
        # B:         <---> <--->
        # C:                 <------>
        # Next try:          |
        next_dt = max(intervals, key=lambda x: x.left).left
        opened = any(
            interv.closed not in ('left', 'both')
            for interv in intervals
            if interv.left == next_dt
        )
        if opened:
            next_dt -= self.resolution
        return self.rollforward(next_dt)

    def __eq__(self, other):
        # self | other
        # bitwise or
        if isinstance(self, type(other)):
            return self.periods == other.periods
        return False

    def __repr__(self):
        sub = ', '.join(repr(p) for p in self.periods)
        return f"All({sub})"

    def __str__(self):
        return ' & '.join(str(p) for p in self.periods)

@dataclass(frozen=True)
class Any(TimePeriod):

    periods: FrozenSet[TimePeriod]

    def __init__(self, *args):
        if any(not isinstance(arg, TimePeriod) for arg in args):
            raise TypeError("Only TimePeriods supported")
        if not args:
            raise ValueError("No TimePeriods to wrap")

        # Compress the time periods
        periods = []
        for arg in args:
            if isinstance(arg, Any):
                # Don't nest unnecessarily
                periods += list(arg.periods)
            elif arg is always:
                # Does not really have an effect
                periods = [always]
                break
            else:
                periods.append(arg)

        object.__setattr__(self, "periods", frozenset(periods))

    def rollback(self, dt):
        intervals = [
            period.rollback(dt)
            for period in self.periods
        ]

        # Example:
        # Current time           |
        # A:    <-------------->
        # B:     <------>
        # C:         <------------->
        # Out:  <------------------>

        # Example:
        # Current time           |
        # A:    <-->
        # B:     <--->     <--->
        # C:     <------>
        # Out:             <--->

        # Example:
        # Current time           |
        # A:    <-->
        # B:    <--->     <--->
        # C:        <----->
        # Out:  <------------->

        # We solve the problem iteratively
        # 1. Find the interval that ends closest to the dt
        # 2. Check if there is an interval overlapping with longer end
        # 3. Repeat 2 until there is none

        # Sorting the closest first (right is oldest)
        intervals = sorted(intervals, key=lambda x: x.right, reverse=True)

        curr_interval = intervals.pop(0)
        end_interval = curr_interval

        for interv in intervals:
            extends = interv.left < curr_interval.left
            if extends and interv.overlaps(curr_interval):
                curr_interval = interv
            else:
                break

        return Interval(
            curr_interval.left,
            end_interval.right
        )

    def rollforward(self, dt):
        intervals = [
            period.rollforward(dt)
            for period in self.periods
        ]

        # We solve the problem iteratively
        # 1. Find the interval that starts closest to the dt
        # 2. Check if there is an interval overlapping with longer end
        # 3. Repeat 2 until there is none

        # Sorting the closest first (left is newest)
        intervals = sorted(intervals, key=lambda x: x.left, reverse=False)

        curr_interval = intervals.pop(0)
        start_interval = curr_interval

        for interv in intervals:
            extends = interv.right > curr_interval.right
            if extends and interv.overlaps(curr_interval):
                curr_interval = interv
            else:
                break

        return Interval(
            start_interval.left,
            curr_interval.right
        )

    def __eq__(self, other):
        # self | other
        # bitwise or
        if isinstance(self, type(other)):
            return self.periods == other.periods
        return False

    def __repr__(self):
        sub = ', '.join(repr(p) for p in self.periods)
        return f"Any({sub})"

    def __str__(self):
        return ' | '.join(str(p) for p in self.periods)

@dataclass(frozen=True)
class StaticInterval(TimePeriod):
    """Interval that is fixed in specific datetimes."""

    start: datetime.datetime
    end: datetime.datetime

    def __init__(self, start=None, end=None):
        object.__setattr__(self, "start", to_datetime(start) if start is not None else self.min)
        object.__setattr__(self, "end", to_datetime(end) if end is not None else self.max)

    def rollback(self, dt):
        dt = to_datetime(dt)
        tz = dt.tzinfo
        start = to_datetime(self.start, timezone=tz)
        if start > dt:
            # The actual interval is in the future
            return Interval(self.min, self.min)
        end = to_datetime(self.end, timezone=tz)
        end = min(end, dt)
        return Interval(start, end)

    def rollforward(self, dt):
        dt = to_datetime(dt)
        end = to_datetime(self.end)
        if end < dt:
            # The actual interval is already gone
            return Interval(self.max, self.max)
        start = max(self.start, dt)
        return Interval(start, end)

    @property
    def is_max_interval(self):
        return (self.start == self.min) and (self.end == self.max)

    def __str__(self):
        if self.is_max_interval:
            return 'always'
        if self.start == self.max:
            return 'never'
        return f'between {self.start} and {self.end}'

    def __repr__(self):
        if self.is_max_interval:
            return 'always'
        if self.start == self.max:
            return 'never'
        return f"StaticInterval(start={self.start!r}, end={self.end!r})"

always = StaticInterval()
never = StaticInterval(StaticInterval.max, StaticInterval.max)
