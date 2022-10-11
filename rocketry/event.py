import datetime
from typing import Any
from pydantic import BaseModel
from rocketry.args import Task
from rocketry.conditions import BaseCondition
from rocketry.core import BaseArgument

class Event(BaseModel):
    datetime: datetime.datetime
    value: Any = None

class EventStream(BaseCondition, BaseArgument):

    def __call__(self, func):
        self.func = func
        return self

    def observe(self, task=Task()):
        event = self._get_last_event()
        if event is None:
            return False
        event_time = event.datetime
        # Check if the event occurred after 
        # previous run of the task
        last_run = task.get_last_run()
        if last_run:
            return last_run < event_time
        else:
            return True

    def get_value(self, **kwargs):
        event = self._get_last_event()
        return event.value

    def _get_last_event(self) -> Event:
        event = self.func()
        if event is None:
            return None
        elif isinstance(event, datetime.datetime):
            event = Event(datetime=event, value=event)
        elif isinstance(event, Event):
            pass
        else:
            event = Event(datetime=datetime.datetime.now(), value=event)
        return event