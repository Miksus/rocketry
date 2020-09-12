
from pypipe.time import period_factory, StaticInterval

import pandas as pd



class _Historical:

    def _init_historical(self):
        self.period = StaticInterval()
        self._before = None
        self._after = None

    def get_time_kwargs(self, dt=None):
        if dt is None:
            dt = self.current_datetime

        interval = self.period.rollback(dt)
        start = interval.left
        end = interval.right

        # self.before(...)
        #    start       end
        #  ---------------<-------t0
        #     EOP       event
        before_start = self._before.get_time_kwargs(dt)["_start_"] if self._before is not None else StaticInterval.min
        before_end = self._before.get_latest_obs() if self._before is not None else StaticInterval.max

        # self.after(...)
        #                 start       end
        #  ----------------->------------------------t0
        #  EOP   event    event       EOP 
        after_start = self._after.get_earliest_obs() if self._after is not None else StaticInterval.min
        after_end = self._after.get_time_kwargs(dt)["_end_"] if self._after is not None else StaticInterval.max

        # If self happened before x? and x never happened --> True if self has happened
        if before_end is None:
            before_end = StaticInterval.max

        # If self happened after x? and x never happened --> False
        if after_start is None:
            raise

        return {"_start_": max(start, before_start, after_start), "_end_": min(end, before_end, after_end)}

    def get_latest_obs(self):
        "Get latest occurence of the event"
        obs = self.function()
        if isinstance(obs, str):
            return pd.Timestamp(obs)
        if len(obs) == 0:
            return None
        return obs[-1]

    def get_earliest_obs(self):
        "Get latest occurence of the event"
        obs = self.function()
        if isinstance(obs, str):
            return pd.Timestamp(obs)
        if len(obs) == 0:
            return None
        return obs[-1]

# Time related
    def between(self, *args, **kwargs):
        return self._set_period(
            period_factory.between(*args, **kwargs)
        )

    def past(self, *args, **kwargs):
        return self._set_period(
            period_factory.past(*args, **kwargs)
        )

    def in_(self, *args, **kwargs):
        return self._set_period(
            period_factory.in_(*args, **kwargs)
        )

    def from_(self, *args, **kwargs):
        return self._set_period(
            period_factory.from_(*args, **kwargs)
        )

    def in_cycle(self, *args, **kwargs):
        return self._set_period(
            period_factory.in_cycle(*args, **kwargs)
        )

    def in_period(self, period):
        return self._set_period(
            period
        )

    def _set_period(self, period):
        stmt = self.copy()
        if not stmt.historical:
            raise TypeError(f"Statement '{stmt.name}' is not historical and does not have past.")
        if isinstance(period, StaticInterval) and period.is_max_interval:
            stmt.period = period
        else:
            stmt.period &= period
        return stmt

    def before(self, obj):
        """Whether the statement is True before the object

        Examples:
            my_statement.before("2020-01-01")
            my_statement.before(mytask)
            >>> before the task has run
            my_statement.before(task_succeeded(task=mytask))
            >>> my_statement.start == None
            >>> my_statement.end == task_succeeded(task=mytask).function()[0]
        """
        if not self.historical:
            raise AttributeError(f"Statement {self} is not historical")

        self._before = obj
        #self.period = FuncInterval(start=None, end=end_func)
        return self

    def after(self, obj):
        """Whether the statement is True before the object

        Examples:
            my_statement.after("2020-01-01")

            my_statement.after(task_succeeded(task=mytask))
            >>> my_statement.start == task_succeeded(task=mytask).function()[-1]
            >>> my_statement.end == None
        """
        if not self.historical:
            raise AttributeError(f"Statement {self} is not historical")
        self._after = obj
        return self


class _Quantitative:
    def _init_quantitative(self):
        self.comparisons = {}

# Comparisons
    def __eq__(self, other):
        # self == other
        obs = self.copy()
        obs._set_comparison("__eq__", other)
        return obs

    def __ne__(self, other):
        # self != other
        obs = self.copy()
        obs._set_comparison("__ne__", other)
        return obs

    def __lt__(self, other):
        # self < other
        obs = self.copy()
        obs._set_comparison("__lt__", other)
        return obs

    def __gt__(self, other):
        # self > other
        obs = self.copy()
        obs._set_comparison("__gt__", other)
        return obs

    def __le__(self, other):
        # self <= other
        obs = copy(self)
        obs._set_comparison("__le__", other)
        return obs
        
    def __ge__(self, other):
        # self >= other
        obs = self.copy()
        obs._set_comparison("__ge__", other)
        return obs

    def more_than(self, num):
        return self > numb

    def less_than(self, num):
        return self < numb

    def _set_comparison(self, key, val):
        if not self.quantitative:
            raise TypeError(f"Statement '{self.name}' is not quantitative and cannot be compared.")
        self.comparisons[key] = val

    def every(self, nth):
        "The statement is true for every nth count of outcomes"
        func = lambda result: (result % nth) == 0

        self._set_comparison("every", func)
# TODO: _set_comparison is just name and function, remove magic methods