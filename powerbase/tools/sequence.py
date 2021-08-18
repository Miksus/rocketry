
import datetime
from powerbase.core import BaseCondition
from powerbase.conditions import Any, All, AlwaysFalse
from powerbase.parse import parse_time

class _SequenceTrigger(BaseCondition):

    def __init__(self, prev_task, task, parent):
        self.prev_task = prev_task
        self.task = task
        self.parent = parent

    def __bool__(self):
        
        now = datetime.datetime.now()
        
        if self.parent.interval is None:
            # prev_task must have been (successfully)
            # run and curr_task has not been run
            # if interval not set
            if self.prev_task.last_success is None:
                return False
            return self.prev_task.last_success > self.curr_task.last_start 

        interval = self.parent.interval
        isin_interval = now in interval
        if not isin_interval:
            return False

        curr_interval = interval.rollback(now)
        return self._is_prev_succeeded(curr_interval) and not self._is_curr_ran(curr_interval)

    def _is_prev_succeeded(self, curr_interval):
        prev_task = self.prev_task
        if prev_task is None:
            # There is no previous task, so it is ok
            return True
        elif prev_task.last_success is None:
            # Has not previously succeeded at all
            return False
        return prev_task.last_success in curr_interval

    def _is_curr_ran(self, curr_interval):
        curr_task = self.task
        if curr_task._last_run is None:
            # Has not run previously
            return False
        elif curr_task._last_run not in curr_interval:
            # Has not run in the interval
            # TODO: use also .last_finish in .interval 
            return False
        else:
            return True


class TriggerCluster(Any):
    pass

class Sequence:

    def __init__(self, tasks:list, interval=None):
        self.tasks = tasks
        self.interval = parse_time(interval) if interval is not None else None
        self.set_conditions()

    def set_conditions(self):
        # task.start_cond & (trigger1 | trigger2 | trigger3)
        prev_task = None
        for task in self.tasks:
            self.add_trigger(task, prev_task=prev_task)
            prev_task = task

    def add_trigger(self, task, prev_task):
        trigger = _SequenceTrigger(task=task, prev_task=prev_task, parent=self)
        if not isinstance(task.start_cond, (Any, All)):
            if isinstance(task.start_cond, AlwaysFalse):
                # Default condition is AlwaysFalse, 
                # we are forgiving and don't require
                # user to give AlwaysTrue in order
                # to the sequence work
                task.start_cond = TriggerCluster(trigger)
            else:
                # Append to existing conditions
                task.start_cond &= TriggerCluster(trigger)
            return
        # There probably is TriggerCluster where this trigger is added
        for cond in task.start_cond:
            if isinstance(cond, TriggerCluster):
                cond.subconditions.append(trigger)
                break
        else:
            task.start_cond &= TriggerCluster(trigger)
