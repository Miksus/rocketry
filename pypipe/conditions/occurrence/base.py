
from ..time import TimeCondition
from ..base import BaseCondition
#from pypipe.event import Event

from pypipe.time import TimeCycle, TimeDelta, TimeInterval




class Occurring(BaseCondition):
    def __init__(self, event):
        self.event = event

    def __bool__(self):
        observation = self.event.observe()
        return bool(observation)

class HasOccurred(TimeCondition):
    # Ideas for naming:
    # EventOccurrence, EventPeriod, Occurrence
    """Whether an event has occured in the past.
    The event must have some sort of memory. 

    HasOccurred(task_ran)

    HasOccurred(task_ran, Daily("10:00"))
    """
    def __init__(self, 
                event, period=None, *, 
                past=None, between=None, freq=None):

        self.event = event
        if period is None:
            period = self.get_time_period(past=past, between=between, freq=freq)
        self.time_period = period


    def __bool__(self):
        dt = self.current_datetime
        item = self.time_period.prev(dt)
        start, end = item.left, item.right
        observations = self.event.observe(start=start, end=end)
        return observations

    def estimate_next(self, dt):
        if bool(self):
            return self.resolution

        if self.time_period.fixed:
            #         dt
            #  -->----------<----------->--------------<-
            #  start       end        start           end
            return self.time_period.rollforward(dt)

    def __repr__(self):
        event = repr(self.event)
        time = (
            f'past {self.time_period}'
            if isinstance(self.time_period, TimeDelta)
            else f'between {self.time_period}'
            if isinstance(self.time_period, TimeInterval)
            else f'from {self.time_period}'
        )

        return f'<has not {repr(self.event)}{time}>'

class HasNotOccurred(TimeCondition):
    """Whether the event has not occured between specified times.
    Note, this condition does not support 
    """
    def __init__(self, 
                event, period=None, *, 
                past=None, between=None, freq=None,
                more_than=None, less_than=None, equal=None):
        self.event = event
        if period is None:
            period = self.get_time_period(past=past, between=between, freq=freq)
        self.time_period = period

    def __bool__(self):
        dt = self.current_datetime
        item = self.time_period.prev(dt)
        start, end = item.left, item.right
        observations = self.event.observe(start=start, end=end)
        return not observations
