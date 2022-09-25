from typing import Callable
from dataclasses import dataclass

from rocketry.core.time.base import TimePeriod, always

from .interval import TimeOfHour, TimeOfDay, TimeOfMinute, TimeOfWeek, TimeOfMonth, TimeOfYear

@dataclass(frozen=True)
class Cron(TimePeriod):

    minute: str = "*"
    hour: str = "*"
    day_of_month: str = "*"
    month: str = "*"
    day_of_week: str = "*"

    def __init__(self, minute="*", hour="*", day_of_month="*", month="*", day_of_week="*"):
        object.__setattr__(self, "minute", minute)
        object.__setattr__(self, "hour", hour)
        object.__setattr__(self, "day_of_month", day_of_month)
        object.__setattr__(self, "month", month)
        object.__setattr__(self, "day_of_week", day_of_week)

        # *: any value
        # ,: list of values
        # -: range of values
        # /: step values

    def rollforward(self, dt):
        "Get previous time interval of the period."
        return self.get_subperiod().rollforward(dt)

    def rollback(self, dt):
        "Get previous time interval of the period."
        return self.get_subperiod().rollback(dt)

    def _get_period_from_expr(self, cls, expression:str, conv:Callable=None, default=always):

        conv = (lambda i: i) if conv is None else conv
        exprs = expression.split(",")
        full_period = None
        for expr in exprs:
            if expr == "*":
                # Any
                continue
            if "/" in expr:
                expr, step = expr.split("/")
                step_period = cls.create_range(step=int(step))
            else:
                step = None

            if "-" in expr:
                # From to
                start, end = expr.split("-")
                if start.isdigit():
                    start = conv(int(start))
                if end.isdigit():
                    end = conv(int(end))

                if step is not None:
                    # Unlike in traditional Python ranges,
                    # cron includes also the endpoint thus
                    # we convert to int (if needed) and add
                    # one
                    if isinstance(end, str):
                        end = cls._unit_mapping[end.lower()]
                    end += 1
                    period = cls.create_range(start, end, step=int(step))
                else:
                    period = cls(start, end)
            else:
                # At
                step_period = cls.create_range(step=int(step)) if step is not None else always
                value = conv(int(expr)) if expr.isdigit() else expr
                if value == "*":
                    period = always & step_period
                else:
                    period = cls.at(value) & step_period

            if full_period is None:
                full_period = period
            else:
                full_period |= period

        if full_period is None:
            return default
        return full_period

    def _convert_day_of_week(self, i:int):
        # In cron, 0 is Sunday but DayOfWeek don't allow zero
        return 7 if i == 0 else i

    def get_subperiod(self):
        minutely = TimeOfMinute()

        day_of_month = self._get_period_from_expr(TimeOfMonth, self.day_of_month)
        day_of_week = self._get_period_from_expr(TimeOfWeek, self.day_of_week, conv=self._convert_day_of_week)

        if day_of_month is not always and day_of_week is not always:
            # Both specified: OR
            day_of_week_month = day_of_month | day_of_week
        else:
            # Either is specified or neither: AND (the other should be "always")
            day_of_week_month = day_of_month & day_of_week

        return (
            (self._get_period_from_expr(TimeOfHour, self.minute) & minutely)
            & self._get_period_from_expr(TimeOfDay, self.hour)
            & self._get_period_from_expr(TimeOfYear, self.month)
            & day_of_week_month
        )
