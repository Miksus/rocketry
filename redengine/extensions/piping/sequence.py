
from typing import List
import datetime

from redengine.core import BaseExtension
from redengine.conditions import AlwaysFalse
from redengine.parse import parse_time, parse_task
from redengine.core.time import TimePeriod
from redengine.core import Task
from .trigger import TriggerCluster, IntervalTrigger, PulseTrigger, BaseTrigger


class Sequence(BaseExtension):
    """Sequence is a task pipe but with exception that 
    each task is run only once in the interval.

    Parameters
    ----------
    tasks : list of :py:class:`redengine.core.Task`
        Tasks that are to be executed in order.
    interval : str, :py:class:`redengine.core.TimePeriod`, optional
        Interval when the sequence is allowed to run. When
        the interval starts, the sequence starts from the 
        first task regardless of previous state. 
    sys_paths : list of path-like, optional
        List of paths that are set to ``sys.path`` temporarily
        to solve possible imports in the script.
    **kwargs : dict
        See :py:class:`redengine.component.BaseComponent`
    """

    __parsekey__ = "sequences"

    triggers: List[BaseTrigger]
    interval: TimePeriod
    tasks: List[Task]

    def at_parse(self, tasks:list, interval=None):
        self.tasks = [parse_task(task, session=self.session) for task in tasks]
        self.interval = parse_time(interval) if interval is not None else None
        self.triggers = []

        for task in self.tasks:
            self.add_task(task)
        if self.interval is None:
            self.close_cycle()

    def add_task(self, task):
        trigger_cls = self.get_trigger_cls()

        depend_trigger = None if not self.triggers else self.triggers[-1]
        trigger = trigger_cls(task=task, depend_trigger=depend_trigger, parent=self)
        self.triggers.append(trigger)
        
        existing_cluster = TriggerCluster.find(task.start_cond)

        if existing_cluster is not None:
            existing_cluster.subconditions.append(trigger)
        else:
            if isinstance(task.start_cond, AlwaysFalse):
                # Default condition is AlwaysFalse, 
                # we are forgiving and don't require
                # user to give AlwaysTrue in order
                # to the sequence work
                task.start_cond = TriggerCluster(trigger, task=task)
            else:
                # Append to existing conditions
                task.start_cond &= TriggerCluster(trigger, task=task)

    def close_cycle(self):
        """If interval is None, add the last trigger as depenency to the 
        first so that the first won't be triggered all the time"""
        self.triggers[0].depend_trigger = self.triggers[-1]

    def get_trigger_cls(self):
        if self.interval is not None:
            return IntervalTrigger
        else:
            return PulseTrigger

    def get_last_run(self):
        return max(self.triggers, key=lambda trg: trg.task.last_run or datetime.datetime.min)

    def delete(self):
        super().delete()
        for trigger in self.triggers:
            trigger.delete()

    def __repr__(self):
        task_names = [task.name for task in self.tasks]
        return f'Sequence(tasks={task_names}, interval={repr(self.interval)})'