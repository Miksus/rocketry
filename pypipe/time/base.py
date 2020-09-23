import datetime
import pandas as pd
# TODO: Way to calculate how much time (ie. seconds) to next event

from abc import abstractmethod
import inspect
import itertools

SYNTAX_MAPPING = {
    "from_": {},
    "in_cycle": {},
    "in_": {}
}

def get_period(name, group):
    periods = PERIOD_CLASSES[group]
    period = [
        period
        for period in periods
        if period.__name__.lower() == name.lower()
    ]
    if len(period) == 0:
        raise ValueError(f"Period {name} from {group} not found. (Options: {periods})")
    return period[0]

def register_class(cls):
    parents = inspect.getmro(cls)
    is_cycle = TimeCycle in parents
    is_interval = TimeInterval in parents
    is_delta = TimeDelta in parents

    n_parents = sum([is_cycle, is_interval, is_delta])
    if n_parents > 1:
        raise TypeError(f"Class {cls} cannot be registered as it inherits from more than one TimePeriod abstract classes")
    elif n_parents < 1:
        raise TypeError(f"Class {cls} cannot be registered as it does not inherit from TimePeriod abstract classes")

    parent = TimeCycle if is_cycle else TimeInterval if is_interval else TimeDelta
    PERIOD_CLASSES[parent].append(cls)

class TimePeriod:
    """Base for all classes that represent a time period

    Time period is a section in time where an event/occurence/current time can be

    Examples:
    ---------
        hour
        time of day (like from 12 am to 4 pm)
        month
    """

    resolution = pd.Timestamp.resolution
    min = pd.Timestamp.min
    max = pd.Timestamp.max

    def __init__(self, *args, **kwargs):
        pass

    def register(self, syntax, group):
        "Save the instance to the register for easier access"
        SYNTAX_MAPPING[group][syntax] = self

    def next_time_span(self, dt, *, include_current=False) -> tuple:
        "Return (start, end) for next "
        # TODO: Remove
        if include_current:
            next_dt = self.rollstart(dt)
            
        return (self.floor(next_dt), self.ceil(next_dt))

    def estimate_timedelta(self, dt):
        "Time for beginning of the next start time of the condition"
        # TODO: Remove
        dt_next_start = self.rollstart(dt)
        return dt_next_start - dt

    def __contains__(self, other):
        interval = self.rollforward(other)
        return other in interval

    def __and__(self, other):
        # self & other
        # bitwise and
        # using & operator

        return All(self, other)

    def __or__(self, other):
        # self | other
        # bitwise or

        return Any(self, other)

    def rollforward(self, dt):
        "Get previous time interval of the period"
        raise NotImplementedError

    def rollback(self, dt):
        "Get previous time interval of the period"
        raise NotImplementedError

    def next(self, dt):
        "Get next interval (excluding currently ongoing if any)"
        interv = self.rollforward(dt)
        if dt in interv:
            # Offsetting the end point with minimum amount to get new full interval
            interv = self.rollforward(dt.right + self.resolution)
        return interv

    def prev(self, dt):
        "Get previous interval (excluding currently ongoing if any)"
        interv = self.rollback(dt)
        if dt in interv:
            # Offsetting the end point with minimum amount to get new full interval
            interv = self.rollback(dt.left - self.resolution)
        return interv

class TimeInterval(TimePeriod):
    """Base for all time intervals

    Time interval is a period between two fixed but repeating 
    times. Fixed repeated times are defined as time elements
    that repeats constantly but are fixed in a sense that
    if the datetime of an event is known, the question
    whether the event belongs to the period can be answered
    unambigiously.

    Examples:
    ---------
        Time of day (ie. from 11 am to 5 pm)
        Month (ie. January)

    Answers to "between 11:00 and 12:00" and "from monday to tuesday"
    """
    _type_name = "interval"
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
    def from_between(start, end):
        raise NotImplementedError("__between__ not implemented.")

    def rollforward(self, dt):
        "Get next time interval of the period"

        start = self.rollstart(dt)
        end = self.next_end(dt)

        start = pd.Timestamp(start)
        end = pd.Timestamp(end)
        
        return pd.Interval(start, end, closed="both")
    
    def rollback(self, dt):
        "Get previous time interval of the period"

        end = self.rollend(dt)
        start = self.prev_start(dt)

        start = pd.Timestamp(start)
        end = pd.Timestamp(end)
        
        return pd.Interval(start, end, closed="both")



class TimeDelta(TimePeriod):
    """Base for all time deltas

    Time delta is a period of time from a reference
    point. It is floating in nature as it could
    contain arbitrary datetimes depending on where
    the reference point is set. This reference
    point is typically current datetime.

    Examples:
    ---------
        hour (ie. one hour in the past)
        day (ie. one day from an event)

    Answers to "past 1 hour"
    """
    _type_name = "delta"
    def __init__(self, *args, **kwargs):
        self.duration = abs(pd.Timedelta(*args, **kwargs))
        if pd.isna(self.duration):
            raise ValueError("TimeDelta duration cannot be 'not a time'")

    @abstractmethod
    def __contains__(self, dt):
        "Check whether the datetime is in "
        start = self.reference - self.duration
        end = self.reference
        return start <= dt <= end

    def rollback(self, dt):
        "Get previous interval (including currently ongoing)"
        start = dt - self.duration
        start = pd.Timestamp(start)
        end = pd.Timestamp(dt)
        return pd.Interval(start, end) 

    def rollforward(self, dt):
        "Get next interval (including currently ongoing)"
        end = dt + self.duration
        start = pd.Timestamp(dt)
        end = pd.Timestamp(end)
        return pd.Interval(start, end)




class TimeCycle(TimePeriod):
    """Base for all time cycles

    Time cycle is a period of time that is constantly
    repeating. It has start time but inherently all
    datetimes belong to the cycle. Useful tool to 
    check whether an event has already 

    Useful for checking times an event has happened
    during the cycle

    Examples:
    ---------
        hourly
        daily
        weekly
        monthly
    """
    _type_name = "cycle"

    offset = None
    def __init__(self, *args, n=1, **kwargs):
        self.start = self.transform_start(*args, **kwargs)
        self.n = n

    def __mul__(self, value):
        return type(self)(self.start, n=value)

    def rollback(self, dt):
        dt_start = dt - (self.n - 1) * self.offset
        if self.get_time_element(dt_start) >= self.start:
            #       dt
            #  -->--------------------->-----------
            #  time   |              time     |    
            pass
        else:
            #               dt
            #  -->--------------------->-----------
            #  time   |              time     |    
            dt_start = dt_start - self.offset
        dt_start = self.replace(dt_start)

        start = pd.Timestamp(dt_start)
        end = pd.Timestamp(dt)

        return pd.Interval(start, end)

    def rollforward(self, dt):
        dt_end = dt + (self.n - 1) * self.offset
        if self.get_time_element(dt_end) >= self.start:
            #       dt           (dt_end)
            #  -->--------------------->-----------
            #  time   |              time     |    
            dt_end = dt_end + self.offset
        else:
            #               dt
            #  -->--------------------->-----------
            #  time   |              time     |    
            pass
        dt_end = self.replace(dt_end)

        start = pd.Timestamp(dt)
        end = pd.Timestamp(dt_end) - self.resolution
        
        return pd.Interval(start, end)

    def rollend(self, dt):
        """All datetimes are in the cycle thus rolls
        returns the same datetime. This method is for
        convenience"""
        return dt

    def rollstart(self, dt):
        """All datetimes are in the cycle thus rolls
        returns the same datetime. This method is for
        convenience"""
        return dt

    @abstractmethod
    def transform_start(self, dt):
        pass

    @abstractmethod
    def get_time_element(self, dt):
        """Extract the time element from a
        datetime.
        Examples:
        ---------
            week cycle: day of week
            day cycle: time of day
            month cycle: day of month"""

    @abstractmethod
    def replace(self, dt):
        """Replace the datetime in a way that it is
        on current cycle's start day. This is to make
        the implementation of cycles less tiresome"""
        #              dt---------->
        #  -->--------------------->-----------
        #  time      |           time     |    
        # OR
        #    <----dt  
        #  -->--------------------->-----------
        #  time      |           time     |    



class All(TimePeriod):

    def __init__(self, *args):
        if any(not isinstance(arg, TimePeriod) for arg in args):
            raise TypeError("All is only supported with TimePeriods")
        self.periods = args

    def rollback(self, dt):
        intervals = [
            period.rollback(dt)
            for period in self.periods
        ]
        if all(a.overlaps(b) for a, b in itertools.combinations(intervals, 2)):
            # All overlaps, can be defined conveniently using max, min
            starts = [interval.left for interval in intervals]
            ends = [interval.right for interval in intervals]

            start = max(starts)
            end = min(ends)
            return pd.Interval(start, end)
        else:
            starts = [interval.left for interval in intervals]
            return self.rollback(max(starts) - datetime.datetime.resolution)

    def rollforward(self, dt):
        intervals = [
            period.rollforward(dt)
            for period in self.periods
        ]
        if all(a.overlaps(b) for a, b in itertools.combinations(intervals, 2)):
            # All overlaps, can be defined conveniently using max, min
            starts = [interval.left for interval in intervals]
            ends = [interval.right for interval in intervals]

            start = max(starts)
            end = min(ends)
            return pd.Interval(start, end)
        else:
            ends = [interval.right for interval in intervals]
            # Tries next interval
            return self.nex(min(ends) + datetime.datetime.resolution)

class Any(TimePeriod):

    def __init__(self, *args):
        if any(not isinstance(arg, TimePeriod) for arg in args):
            raise TypeError("Any is only supported with TimePeriods")
        self.periods = args

    def rollback(self, dt):
        intervals = [
            period.rollback(dt)
            for period in self.periods
        ]
        starts = [interval.left for interval in intervals]
        ends = [interval.right for interval in intervals]

        start = min(starts)
        end = max(ends)
        return pd.Interval(start, end)

    def rollforward(self, dt):
        intervals = [
            period.rollforward(dt)
            for period in self.periods
        ]
        starts = [interval.left for interval in intervals]
        ends = [interval.right for interval in intervals]

        start = min(starts)
        end = max(ends)
        return pd.Interval(start, end)

class Offsetted(TimePeriod):

    def __init__(self, period, n):
        if isinstance(period, TimeCycle):
            # adjust prev & next
            raise NotImplementedError
        self.period = period
        self.n = n

    def rollback(self, dt):
        interval = self.period.rollback(dt)
        new_dt = interval.left - pd.Timestamp.resolution
        interval = self.period.rollback(new_dt)
        return interval

    def rollforward(self, dt):
        interval = self.period.rollforward(dt)
        new_dt = interval.right + pd.Timestamp.resolution
        interval = self.period.rollforward(new_dt)
        return interval

class StaticInterval(TimePeriod):
    """Inverval that is fixed in specific datetimes
    """

    def __init__(self, start=None, end=None):
        self.start = start if start is not None else self.min
        self.end = end if end is not None else self.max

    def rollback(self, dt):
        dt = pd.Timestamp(dt)
        start = pd.Timestamp(self.start)
        if start > dt:
            # The actual interval is in the future
            return pd.Interval(self.min, self.min)
        return pd.Interval(start, dt)

    def rollforward(self, dt):
        dt = pd.Timestamp(dt)
        end = pd.Timestamp(self.end)
        if end < dt:
            # The actual interval is already gone
            return pd.Interval(self.max, self.max)
        return pd.Interval(dt, end)

    @property
    def is_max_interval(self):
        return (self.start == self.min) and (self.end == self.max)

PERIOD_CLASSES = {
    TimeCycle: [],
    TimeDelta: [],
    TimeInterval: [],
}