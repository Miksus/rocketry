from rocketry.args.builtin import Session
from rocketry.core.condition.base import BaseComparable, BaseCondition
from rocketry.core.time.utils import get_period_span


class SchedulerCycles(BaseComparable):
    """Condition for whether the scheduler have had
    more/less/equal given amount of cycles of executing
    tasks.
    """

    def get_measurement(self, session=Session()) -> int:
        n_cycles = session.scheduler.n_cycles
        return n_cycles

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        comps = {
            "__eq__": "has",
            "__gt__": "has more than",
            "__lt__": "has less than",
            "__ge__": "has more or equal than",
            "__le__": "has less or equal than",
        }
        s = "scheduler"
        for key, val in self._comps.items():
            s = s + " " + comps.get(key, key) + " " + str(val) + " cycles"
        return s

    @classmethod
    def from_magic(cls, **kwargs):
        kwargs = {key: int(value) for key, value in kwargs.items()}
        return super(SchedulerCycles, cls).from_magic(**kwargs)

class SchedulerStarted(BaseCondition):
    """Condition for whether the scheduler had started
    in given period.

    Examples
    --------

    **Parsing example:**

    >>> from rocketry.parse import parse_condition
    >>> parse_condition("scheduler started 10 minutes ago")
    SchedulerStarted(period=TimeDelta('10 minutes'))

    >>> parse_condition("scheduler has run over 10 minutes")
    ~SchedulerStarted(period=TimeDelta('10 minutes'))
    """

    def __init__(self, period=None):
        self.period = period
        super().__init__()

    def get_state(self, session=Session()) -> bool:
        start, end = get_period_span(self.period, session=session)
        dt = session.scheduler.startup_time
        return start <= dt <= end

    def __str__(self):
        if hasattr(self, "_str"):
            return self._str
        return f"scheduler {self.period}"
