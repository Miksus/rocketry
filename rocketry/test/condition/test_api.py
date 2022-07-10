import pytest

from rocketry.conds import (
    true, false,
    minutely, hourly, daily, weekly, monthly,
    time_of_minute, time_of_hour, time_of_day, time_of_week, time_of_month,
    after_finish, after_success, after_fail
)

from rocketry.conditions import TaskExecutable, IsPeriod, DependSuccess, DependFailure, DependFinish
from rocketry.core.condition.base import AlwaysFalse, AlwaysTrue
from rocketry.time.interval import TimeOfDay, TimeOfHour, TimeOfMinute, TimeOfMonth, TimeOfWeek

params_basic = [
    pytest.param(true, AlwaysTrue(), id="true"),
    pytest.param(false, AlwaysFalse(), id="false"),
]

params_time = [
    pytest.param(time_of_hour.after("45:00"), IsPeriod(period=TimeOfHour("45:00", None)), id="time of hour after"),

    pytest.param(time_of_day.after("10:00"), IsPeriod(period=TimeOfDay("10:00", None)), id="time of day after"),
    pytest.param(time_of_day.before("10:00"), IsPeriod(period=TimeOfDay(None, "10:00")), id="time of day before"),
    pytest.param(time_of_day.between("10:00", "12:00"), IsPeriod(period=TimeOfDay("10:00", "12:00")), id="time of day between"),

    pytest.param(time_of_week.on("Monday"), IsPeriod(period=TimeOfWeek("Mon", time_point=True)), id="time of week on"),
    pytest.param(time_of_month.between("1st", "5th"), IsPeriod(period=TimeOfMonth("1st", "5th")), id="time of month between"),
]

params_task_exec = [
    pytest.param(minutely.after("45:00"), TaskExecutable(period=TimeOfMinute("45:00", None)), id="minutely after"),
    pytest.param(minutely.before("45:00"), TaskExecutable(period=TimeOfMinute(None, "45:00")), id="minutely before"),

    pytest.param(hourly.after("10:00"), TaskExecutable(period=TimeOfHour("10:00", None)), id="hourly after"),
    pytest.param(hourly.before("10:00"), TaskExecutable(period=TimeOfHour(None, "10:00")), id="hourly before"),
    pytest.param(hourly.between("10:00", "12:00"), TaskExecutable(period=TimeOfHour("10:00", "12:00")), id="hourly between"),
    pytest.param(hourly.starting("10:00"), TaskExecutable(period=TimeOfHour("10:00", "10:00")), id="hourly starting"),

    pytest.param(daily.between("10:00", "12:00"), TaskExecutable(period=TimeOfDay("10:00", "12:00")), id="daily between"),

    pytest.param(weekly.on("Monday"), TaskExecutable(period=TimeOfWeek("Monday", time_point=True)), id="weekly on"),

    pytest.param(monthly.on("1st"), TaskExecutable(period=TimeOfMonth("1st", time_point=True)), id="monthly on"),
]

params_pipeline = [
    pytest.param(after_finish("other"), DependFinish(depend_task="other"), id="after finish"),
    pytest.param(after_success("other"), DependSuccess(depend_task="other"), id="after success"),
    pytest.param(after_fail("other"), DependFailure(depend_task="other"), id="after fail"),
]


@pytest.mark.parametrize(
    "cond,result",
    params_basic + params_time + params_task_exec + params_pipeline
)
def test_api(cond, result):
    assert cond == result