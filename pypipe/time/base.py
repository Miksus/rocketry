import datetime
import pandas as pd
# TODO: Way to calculate how much time (ie. seconds) to next event

from abc import abstractmethod


PERIODS = {
    "cycle": {},
    "delta": {},
    "interval": {},
}

def get_cycle(name):
    return PERIODS["cycle"][name]

def get_delta(name):
    return PERIODS["delta"][name]

def get_interval(name):
    return PERIODS["interval"][name]


class TimePeriod:
    """Base for all classes that represent a time period

    Time period is a section in time where an event/occurence/current time can be

    Examples:
    ---------
        hour
        time of day (like from 12 am to 4 pm)
        month
    """

    def __init__(self, *args, **kwargs):
        pass

    def __new__(cls, *args, **kwargs):
        "Store created cycle for easy acquisition"
        instance = super().__new__(cls)
        period_name = kwargs.get("access_name", None)
        if period_name is None:
            return instance
        else:
            cls_name = cls._type_name
            if period_name in PERIODS[cls_name]:
                raise KeyError(f"All periods must have unique names. Given: {period_name}")

            PERIODS[cls_name][period_name] = instance
            return instance

    def next_time_span(self, dt, *, include_current=False) -> tuple:
        "Return (start, end) for next "
        if include_current:
            next_dt = self.rollforward(dt)
            
        return (self.floor(next_dt), self.ceil(next_dt))

    def estimate_timedelta(self, dt):
        "Time for beginning of the next start time of the condition"
        dt_next_start = self.rollforward(dt)
        return dt_next_start - dt

    def next_span(self, dt):
        start = self.rollforward(dt)
        end = self.next_end(start)
        return pd.Interval(start, end, closed="neither")


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

    """
    _type_name = "interval"
    @abstractmethod
    def __contains__(self, dt):
        "Check whether the datetime is on the period"
        raise NotImplementedError("Contains not implemented.")

    @abstractmethod
    def rollforward(self, dt):
        "Roll forward to next point in time that on the period"
        raise NotImplementedError("Contains not implemented.")

    @abstractmethod
    def rollback(self, dt):
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

    def next(self, dt):
        "Get next time interval of the period"
        start = self.rollforward(dt)
        end = self.next_end(dt)

        start = pd.Timestamp(start)
        end = pd.Timestamp(end)
        
        return pd.Interval(start, end, closed="neither")
    
    def prev(self, dt):
        "Get next time interval of the period"
        end = self.rollback(dt)
        start = self.prev_start(dt)

        start = pd.Timestamp(start)
        end = pd.Timestamp(end)
        
        return pd.Interval(start, end, closed="neither")

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
    """
    _type_name = "delta"
    def __init__(self, *args, access_name=None, **kwargs):
        self.duration = abs(pd.Timedelta(*args, **kwargs))

    @abstractmethod
    def __contains__(self, dt):
        "Check whether the datetime is in "
        start = self.reference - self.duration
        end = self.reference
        return start <= dt <= end

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
    def __init__(self, start=None, n=1, **kwags):
        self.start = self.transform_start(start)
        self.n = n

    def __mul__(self, value):
        return type(self)(self.time, n=value)

    def prev(self, dt):
        dt_start = dt - (self.n - 1) * self.offset
        if self.get_time_element(dt_start) > self.start:
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

    def next(self, dt):
        dt_end = dt - (self.n - 1) * self.offset
        if self.get_time_element(dt_end) > self.start:
            #       dt
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
        end = pd.Timestamp(dt_end)
        
        return pd.Interval(start, end)

    def rollback(self, dt):
        """All datetimes are in the cycle thus rolls
        returns the same datetime. This method is for
        convenience"""
        return dt

    def rollforward(self, dt):
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