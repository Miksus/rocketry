import pytest
from rocketry.conditions.scheduler import SchedulerCycles, SchedulerStarted
from rocketry.conditions.task.task import TaskFailed, TaskFinished, TaskRunning, TaskStarted, TaskSucceeded

from rocketry.conds import (
    true, false,
    every,
    secondly, minutely, hourly, daily, weekly, monthly,
    time_of_second, time_of_minute, time_of_hour, time_of_day, time_of_week, time_of_month,
    after_finish, after_success, after_fail,

    after_all_success, after_any_success, after_all_fail, after_any_fail, after_all_finish, after_any_finish,

    scheduler_running, scheduler_cycles,

    succeeded, failed, finished, started,
    running,

    cron,
    retry,
    crontime,
)

from rocketry.conditions import TaskExecutable, IsPeriod, DependSuccess, DependFailure, DependFinish, TaskRunnable, Retry
from rocketry.core.condition import AlwaysFalse, AlwaysTrue, Any, All
from rocketry.time import TimeDelta
from rocketry.time import Cron
from rocketry.time.delta import TimeSpanDelta
from rocketry.tasks import FuncTask
from rocketry.time.interval import TimeOfDay, TimeOfHour, TimeOfMinute, TimeOfMonth, TimeOfSecond, TimeOfWeek

params_basic = [
    pytest.param(true, AlwaysTrue(), id="true"),
    pytest.param(false, AlwaysFalse(), id="false"),
]

params_time = [
    pytest.param(time_of_second.starting(500), IsPeriod(period=TimeOfSecond.starting(500)), id="time of second starting"),
    pytest.param(time_of_minute.starting(45.00), IsPeriod(period=TimeOfMinute.starting(45.00)), id="time of minute starting"),
    pytest.param(time_of_hour.after("45:00"), IsPeriod(period=TimeOfHour("45:00", None)), id="time of hour after"),

    pytest.param(time_of_day.after("10:00"), IsPeriod(period=TimeOfDay("10:00", None)), id="time of day after"),
    pytest.param(time_of_day.before("10:00"), IsPeriod(period=TimeOfDay(None, "10:00")), id="time of day before"),
    pytest.param(time_of_day.between("10:00", "12:00"), IsPeriod(period=TimeOfDay("10:00", "12:00")), id="time of day between"),

    pytest.param(time_of_week.on("Monday"), IsPeriod(period=TimeOfWeek("Mon", time_point=True)), id="time of week on"),
    pytest.param(time_of_month.between("1st", "5th"), IsPeriod(period=TimeOfMonth("1st", "5th")), id="time of month between"),
]

params_task_exec = [
    pytest.param(every("10 mins"), TaskStarted(period=TimeDelta("10 mins")) == 0, id="every"),
    pytest.param(every("10 mins", based="finish"), TaskExecutable(period=TimeDelta("10 mins")), id="every (finish)"),
    pytest.param(every("10 mins", based="success"), TaskSucceeded(period=TimeDelta("10 mins")) == 0, id="every (success)"),
    pytest.param(every("10 mins", based="fail"), TaskFailed(period=TimeDelta("10 mins")) == 0, id="every (fail)"),

    pytest.param(secondly.get_cond(), TaskExecutable(period=TimeOfSecond(None, None)), id="secondly"),
    pytest.param(minutely.get_cond(), TaskExecutable(period=TimeOfMinute(None, None)), id="minutely"),
    pytest.param(hourly.get_cond(), TaskExecutable(period=TimeOfHour(None, None)), id="hourly"),
    pytest.param(daily.get_cond(), TaskExecutable(period=TimeOfDay(None, None)), id="daily"),
    pytest.param(weekly.get_cond(), TaskExecutable(period=TimeOfWeek(None, None)), id="weekly"),

    pytest.param(minutely.after("45:00"), TaskExecutable(period=TimeOfMinute("45:00", None)), id="minutely after"),
    pytest.param(minutely.before("45:00"), TaskExecutable(period=TimeOfMinute(None, "45:00")), id="minutely before"),

    pytest.param(hourly.after("10:00"), TaskExecutable(period=TimeOfHour("10:00", None)), id="hourly after"),
    pytest.param(hourly.before("10:00"), TaskExecutable(period=TimeOfHour(None, "10:00")), id="hourly before"),
    pytest.param(hourly.between("10:00", "12:00"), TaskExecutable(period=TimeOfHour("10:00", "12:00")), id="hourly between"),
    pytest.param(hourly.starting("10:00"), TaskExecutable(period=TimeOfHour("10:00", "10:00")), id="hourly starting"),

    pytest.param(daily.between("10:00", "12:00"), TaskExecutable(period=TimeOfDay("10:00", "12:00")), id="daily between"),

    pytest.param(secondly.at("45"), TaskExecutable(period=TimeOfSecond("45", "46")), id="minutely at"),
    pytest.param(minutely.at("45"), TaskExecutable(period=TimeOfMinute("45", "46")), id="minutely at"),
    pytest.param(hourly.at("30:00.0000"), TaskExecutable(period=TimeOfHour("30:00", "31:00")), id="hourly at"),
    pytest.param(daily.at("10:00:00"), TaskExecutable(period=TimeOfDay("10:00", "11:00")), id="daily at"),
    pytest.param(weekly.at("Monday"), TaskExecutable(period=TimeOfWeek("Monday", time_point=True)), id="weekly at"),
    pytest.param(monthly.at("1st"), TaskExecutable(period=TimeOfMonth("1st", time_point=True)), id="monthly at"),

    pytest.param(weekly.on("Monday"), TaskExecutable(period=TimeOfWeek("Monday", time_point=True)), id="weekly on"),
    pytest.param(monthly.on("1st"), TaskExecutable(period=TimeOfMonth("1st", time_point=True)), id="monthly on"),

    pytest.param(daily.at("23:00:00"), TaskExecutable(period=TimeOfDay("23:00:00", "00:00:00")), id="daily at end"),
    pytest.param(daily.at("23:00:01"), TaskExecutable(period=TimeOfDay("23:00:01", "00:00:01")), id="daily at specific"),
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

params_action = [
    pytest.param(failed.get_cond(), TaskFailed(task=None), id="has failed (self)"),
    pytest.param(succeeded.get_cond(), TaskSucceeded(task=None), id="has succeeded (self)"),
    pytest.param(started.get_cond(), TaskStarted(task=None), id="has started (self)"),
    pytest.param(finished.get_cond(), TaskFinished(task=None), id="has finished (self)"),

    pytest.param(failed("a_task").get_cond(), TaskFailed(task="a_task"), id="has failed"),
    pytest.param(succeeded("a_task").get_cond(), TaskSucceeded(task="a_task"), id="has succeeded"),
    pytest.param(started("a_task").get_cond(), TaskStarted(task="a_task"), id="has started"),
    pytest.param(finished("a_task").get_cond(), TaskFinished(task="a_task"), id="has finished"),

    pytest.param(started("a_task").this_minute.get_cond(), TaskStarted(task="a_task", period=TimeOfMinute()), id="has started (this minute)"),
    pytest.param(failed("a_task").this_day.get_cond(), TaskFailed(task="a_task", period=TimeOfDay()), id="has failed (this day)"),
    pytest.param(succeeded("a_task").today.between("12:00", "15:00"), TaskSucceeded(task="a_task", period=TimeOfDay("12:00", "15:00")), id="has succeeded (today between)"),
    pytest.param(finished("a_task").this_day.between("12:00", "15:00"), TaskFinished(task="a_task", period=TimeOfDay("12:00", "15:00")), id="has finished (this day between)"),
    pytest.param(started("a_task").this_week.get_cond(), TaskStarted(task="a_task", period=TimeOfWeek()), id="has started (this week)"),
    pytest.param(succeeded("a_task").this_week.before("Mon"), TaskSucceeded(task="a_task", period=TimeOfWeek(None, "Mon")), id="has succeeded (this week before)"),

    pytest.param(retry.get_cond(), Retry(n=-1), id="Retry infinite"),
    pytest.param(retry(2), Retry(n=2), id="Retry twice"),
]

params_running = [
    pytest.param(running.get_cond(), TaskRunning(task=None), id="is running"),
    pytest.param(running(task="mytask").get_cond(), TaskRunning(task="mytask"), id="is running (task)"),
    pytest.param(running("mytask").get_cond(), TaskRunning(task="mytask"), id="is running (task posarg)"),
    pytest.param(running("mytask").more_than("10 mins"), TaskRunning(task="mytask", period=TimeSpanDelta(near="10 mins")), id="is running more than"),
    pytest.param(running("mytask").less_than("10 mins"), TaskRunning(task="mytask", period=TimeSpanDelta(far="10 mins")), id="is running more than"),
    pytest.param(running("mytask").between("15 mins", "20 mins"), TaskRunning(task="mytask", period=TimeSpanDelta(near="15 mins", far="20 mins")), id="is running between"),

    pytest.param(running("mytask") < 2, TaskRunning(task="mytask") < 2, id="is running less than twice"),
    pytest.param(running("mytask") > 2, TaskRunning(task="mytask") > 2, id="is running more than twice"),
    pytest.param(running("mytask") <= 2, TaskRunning(task="mytask") <= 2, id="is running less equal than twice"),
    pytest.param(running("mytask") >= 2, TaskRunning(task="mytask") >= 2, id="is running more equal than twice"),
    pytest.param(running("mytask") == 1, TaskRunning(task="mytask") == 1, id="is running once"),
    pytest.param(running("mytask") != 1, TaskRunning(task="mytask") != 1, id="is running not once"),
]

params_schedule = [
    pytest.param(scheduler_running("10 mins"), SchedulerStarted(period=TimeSpanDelta("10 mins")), id="scheduler running (at least)"),
    pytest.param(scheduler_cycles(5), SchedulerCycles() > 5, id="scheduler cycles (at least)"),
    pytest.param(scheduler_cycles(less_than=5), SchedulerCycles() < 5, id="scheduler cycles (less than)"),
    pytest.param(scheduler_cycles(1, 5), (SchedulerCycles() > 1) < 5, id="scheduler cycles (between)"),
]

cron_like = [
    pytest.param(cron("1 2 3 4 5"), TaskRunnable(period=Cron('1', '2', '3', '4', '5')), id="cron 1 2 3 4 5"),
    pytest.param(cron(minute="1", hour="2", day_of_month="3", month="4", day_of_week="5"), TaskRunnable(period=Cron('1', '2', '3', '4', '5')), id="cron 1 2 3 4 5 (kwargs)"),

    pytest.param(crontime("1 2 3 4 5"), IsPeriod(period=Cron('1', '2', '3', '4', '5')), id="crontime 1 2 3 4 5"),
    pytest.param(crontime(minute="1", hour="2", day_of_month="3", month="4", day_of_week="5"), IsPeriod(period=Cron('1', '2', '3', '4', '5')), id="crontime 1 2 3 4 5 (kwargs)"),
]

@pytest.mark.parametrize(
    "cond,result",
    params_basic + params_time + params_task_exec + params_pipeline + params_action + params_running+ params_schedule + cron_like
)
def test_api(cond, result):
    assert cond == result

@pytest.mark.parametrize(
    "cond",
    [
        pytest.param(retry, id="Retry"),
        pytest.param(finished, id="Finished"),
        pytest.param(daily, id="Daily"),
    ]
)
def test_observe(cond, session):
    # NOTE: We test that observe does not crash (not the output)
    task = FuncTask(func=lambda: None, name="mytask", session=session)

    cond.observe(task=task, session=session)

@pytest.mark.parametrize(
    "get_cond,expected",
    [
        pytest.param(lambda:running(), TaskRunning(task=None), id="is running (call)"),
        pytest.param(lambda:running(more_than="10 mins"), TaskRunning(task=None, period=TimeSpanDelta(near="10 mins")), id="is running 10 mins"),
        pytest.param(lambda:running(more_than="10 mins", task="a_task"), TaskRunning(task="a_task", period=TimeSpanDelta(near="10 mins")), id="is running 10 mins (passed task)"),
    ]
)
def test_deprecated(get_cond, expected, session):
    # NOTE: We test that observe does not crash (not the output)
    with pytest.warns(DeprecationWarning):
        cond = get_cond()
    assert cond == expected

def test_fail():
    with pytest.raises(ValueError):
        every("5 seconds", based="oops")
