import pytest

from rocketry.conds import (
    true, false,
    minutely, hourly, daily, weekly, monthly,
    time_of_minute, time_of_hour, time_of_day, time_of_week, time_of_month,
    after_finish, after_success, after_fail,

    after_all_success, after_any_success, after_all_fail, after_any_fail, after_all_finish, after_any_finish,
)

from rocketry.conditions import TaskExecutable, IsPeriod, DependSuccess, DependFailure, DependFinish
from rocketry.core.condition import AlwaysFalse, AlwaysTrue, Any, All
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

    pytest.param(after_all_finish("do_a", "do_b"), All(DependFinish(depend_task="do_a"), DependFinish(depend_task="do_b")), id="after all finish"),
    pytest.param(after_all_success("do_a", "do_b"), All(DependSuccess(depend_task="do_a"), DependSuccess(depend_task="do_b")), id="after all success"),
    pytest.param(after_all_fail("do_a", "do_b"), All(DependFailure(depend_task="do_a"), DependFailure(depend_task="do_b")), id="after all fail"),

    pytest.param(after_any_finish("do_a", "do_b"), Any(DependFinish(depend_task="do_a"), DependFinish(depend_task="do_b")), id="after any finish"),
    pytest.param(after_any_success("do_a", "do_b"), Any(DependSuccess(depend_task="do_a"), DependSuccess(depend_task="do_b")), id="after any success"),
    pytest.param(after_any_fail("do_a", "do_b"), Any(DependFailure(depend_task="do_a"), DependFailure(depend_task="do_b")), id="after any fail"),
]


@pytest.mark.parametrize(
    "cond,result",
    params_basic + params_time + params_task_exec + params_pipeline
)
def test_api(cond, result):
    assert cond == result