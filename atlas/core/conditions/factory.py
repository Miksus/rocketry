
import calendar
import re

from atlas.conditions.statement import TaskStarted, TaskFailed, task_finished, TaskSucceeded
from atlas.time.factory import period_factory
from atlas.time import (
    TimeOfMinute, TimeOfHour, TImeOfDay,
    TimeDelta
)

from .base import BaseCondition, TimeCondition

from functools import partial


def _set_interval(type_, start=None, end=None):
    type_ = type_.lower()
    cls = {
        "daily": TImeOfDay,
        #"weekly": Weekly,
        "hourly": TimeOfHour,
        "minutely": TimeOfMinute,
    }[type_]

    period = cls(start, end)
    stmt.period = period
    return stmt

def _set_full_interval(type_, start=None, end=None, stmt=None):
    type_ = type_.lower()
    cls = {
        "daily": TImeOfDay,
        #"weekly": Weekly,
        "hourly": TimeOfHour,
        "minutely": TimeOfMinute,
    }[type_]

    # Full cycle with starting point
    period = cls.from_starting(start)
    stmt.period = period
    return stmt


def _get_interval(type_, start=None, end=None):
    type_ = type_.lower()
    cls = {
        "daily": TimeOfDay,
        "weekly": DaysOfWeek,
        "hourly": TimeOfHour,
    }[type_]
    return cls(start=start, end=end)

def _set_delta(value, stmt):
    period = TimeDelta(value)
    stmt.period = period
    return stmt



def _get_is_time_of(type_, start=None, end=None):
    type_ = type_.lower()
    cls = {
        "daily": TimeOfDay,
        "weekly": DaysOfWeek,
        "hourly": TimeOfHour,
    }[type_]
    period = cls(start, end)
    return period_to_condition(period)

def _get_retry(value):
    TaskStarted.set_period()


class _ConditionFactory:

    # Expressions for dynamic string parameters
    expressions = [
        (r"after task '(?P<task>.+)'",      task_finished),
        (r"after finished '(?P<task>.+)'",  task_finished),

        (r"after failed '(?P<task>.+)'",    TaskFailed),
        (r"after succeeded '(?P<task>.+)'", TaskSucceeded),
        (r"after started '(?P<task>.+)'",   TaskStarted),

        # Time and task related
        (r"(run )?(?P<type_>monthly|weekly|daily|hourly|minutely) starting (?P<start>.+)", partial(_set_full_interval, stmt=TaskStarted)),
        # (r"(?P<type_>monthly|weekly|daily|hourly|minutely) ending (?P<end>.+)", _get_cycle),

        (r"(run )?(?P<type_>monthly|weekly|daily|hourly|minutely) between (?P<start>.+) and (?P<end>.+)", partial(_set_interval, stmt=TaskStarted),
        (r"(run )?(?P<type_>monthly|weekly|daily|hourly|minutely) after (?P<start>.+)", partial(_set_interval, stmt=TaskStarted)),
        (r"(run )?(?P<type_>monthly|weekly|daily|hourly|minutely) before (?P<end>.+)", partial(_set_interval, stmt=TaskStarted)),

        (r"(run )?(?P<type_>monthly|weekly|daily|hourly|minutely)", partial(_set_interval, stmt=TaskStarted))),
        (r"(run )?every (?P<value>.+)", partial(_set_delta, stmt=TaskStarted)),

        (r"when time of (?P<type_>month|week|day|hour|minute) between (?P<start>.+) and (?P<end>.+)", _get_is_time_of),
        (r"when time of (?P<type_>month|week|day|hour|minute) after (?P<start>.+)", _get_is_time_of),
        (r"when time of (?P<type_>month|week|day|hour|minute) before (?P<end>.+)", _get_is_time_of),

        # Failure/Success
        (r"try (?P<value>[0-9]+) times", ???),
        (r"(?P<type_>failed|succeeded) (?P<comparison>less than|more than) (?P<value>[0-9]+) times in a row", ???),
    ]

    def parse_str(self, s):


    def _parse_statement_string(self, s):
        expressions = self.expressions
        
        for expr, func in expressions:
            res = re.search(expr, s, flags=re.IGNORECASE)
            if res:
                output =  func(**res.groupdict())
                break
        else:
            raise ValueError(f"Unknown conversion for: {s}")
        return output


    def how(self, s:str):
        """
        """
        statements = self._tokenize(s)

    def _parse_statement(self, s:str) -> BaseCondition:
        for expr, func in self.expressions:
            res = re.search(expr, s, flags=re.IGNORECASE)
            if res:
                output =  func(**res.groupdict())
                break
        else:
            raise ValueError(f"Unknown conversion for: {s}")
        
        if isinstance(output, Period):
            # output is atlas.time...
            output = PeriodCondition(output)
        return output


condition_factory = _ConditionFactory()