import datetime
import pytest
from rocketry.time import Cron
from rocketry.time.interval import TimeOfDay, TimeOfHour, TimeOfMinute, TimeOfMonth, TimeOfWeek, TimeOfYear

every_minute = TimeOfMinute()

@pytest.mark.parametrize(
    "period,expected",
    [
        # Test at
        pytest.param(Cron(), every_minute, id="* * * * *"),
        pytest.param(Cron("30", "*", "*", "*", "*"), every_minute & TimeOfHour.at(30), id="30 * * * *"),
        pytest.param(Cron("*", "12", "*", "*", "*"), every_minute & TimeOfDay.at(12), id="* 12 * * *"),
        pytest.param(Cron("*", "*", "28", "*", "*"), every_minute & TimeOfMonth.at(28), id="* * 28 * *"),
        pytest.param(Cron("*", "*", "*", "6", "*"), every_minute & TimeOfYear.at(6), id="* * * 6 *"),
        pytest.param(Cron("*", "*", "*", "*", "0"), every_minute & TimeOfWeek.at("Sunday"), id="* * * * 0"),

        # Test at synonyms
        pytest.param(Cron("*", "*", "*", "JUN", "*"), every_minute & TimeOfYear.at("June"), id="* * * JUN *"),
        pytest.param(Cron("*", "*", "*", "*", "SUN"), every_minute & TimeOfWeek.at("Sunday"), id="* * * * SUN"),

        # Test ranges
        pytest.param(Cron("45-59", "*", "*", "*", "*"), every_minute & TimeOfHour(45, 59), id="45-59 * * * *"),
        pytest.param(Cron("*", "10-13", "*", "*", "*"), every_minute & TimeOfDay(10, 13), id="* 10-13 * * *"),
        pytest.param(Cron("*", "*", "28-30", "*", "*"), every_minute & TimeOfMonth(28, 30), id="* * 28-30 * *"),
        pytest.param(Cron("*", "*", "*", "FEB-MAR", "*"), every_minute & TimeOfYear("feb", "mar"), id="* * * FEB-MAR *"),
        pytest.param(Cron("*", "*", "*", "*", "FRI-SUN"), every_minute & TimeOfWeek("fri", "sun"), id="* * * * FRI-SUN"),

        # Test list
        pytest.param(Cron("0,15,30,45", "*", "*", "*", "*"), every_minute & (TimeOfHour.at(0) | TimeOfHour.at(15) | TimeOfHour.at(30) | TimeOfHour.at(45)), id="0,15,30,45 * * * *"),

        # Test combinations
        pytest.param(
            Cron("45-59", "10-13", "28-30", "FEB-MAR", "FRI-SUN"),
            every_minute & TimeOfHour(45, 59) & TimeOfDay(10, 13) & TimeOfYear("feb", "mar") & (TimeOfMonth(28, 30) | TimeOfWeek("fri", "sun")),
            id="45-59 10-13 28-30 FEB-MAR FRI-SUN"
        ),
        pytest.param(
            Cron("45-59", "10-13", "28-30", "FEB-MAR", "*"),
            every_minute & TimeOfHour(45, 59) & TimeOfDay(10, 13) & TimeOfYear("feb", "mar") & TimeOfMonth(28, 30),
            id="45-59 10-13 28-30 FEB-MAR *"
        ),
        pytest.param(
            Cron("0-29,45-59", "0-10,20-23", "*", "*", "*"),
            (TimeOfHour(0, 29) | TimeOfHour(45, 59)) & (TimeOfDay(0, 10) | TimeOfDay(20, 23)) & every_minute,
            id="0-29,45-59 0-10,20-23 * * *"
        ),

        # Test skip
        pytest.param(
            Cron("*/15", "*", "*", "*", "*"),
            every_minute & (
                TimeOfHour.at("00:00") | TimeOfHour.at("15:00") | TimeOfHour.at("30:00") | TimeOfHour.at("45:00")
            ),
            id="*/15 * * * *"
        ),
        pytest.param(
            Cron("*", "*/6", "*", "*", "*"),
            every_minute & (
                TimeOfDay.at("00:00") | TimeOfDay.at("06:00") | TimeOfDay.at("12:00") | TimeOfDay.at("18:00")
            ),
            id="* */6 * * *"
        ),
        pytest.param(
            Cron("*", "2-17/6", "*", "*", "*"),
            every_minute & (
                TimeOfDay.at("02:00") | TimeOfDay.at("08:00") | TimeOfDay.at("14:00")
            ),
            id="* 2-17/6 * * *"
        ),
        pytest.param(
            Cron("*", "*", "*", "*", "Tue-Fri/2"),
            every_minute & (
                TimeOfWeek.at("Tue") | TimeOfWeek.at("Thu")
            ),
            id="* * * * Tue-Fri/2"
        ),
        pytest.param(
            Cron("*", "*", "*", "Feb-Aug/3", "*"),
            every_minute & (
                TimeOfYear.at("Feb") | TimeOfYear.at("May") | TimeOfYear.at("Aug")
            ),
            id="* * * Feb-Aug/3 *"
        ),
    ]
)
def test_subperiod(period, expected):
    subperiod = period.get_subperiod()
    assert subperiod == expected

def test_in():
    period = Cron("30", "*", "*", "*", "*")
    assert datetime.datetime(2022, 8, 7, 12, 29, 59) not in period
    assert datetime.datetime(2022, 8, 7, 12, 30, 00) in period
    assert datetime.datetime(2022, 8, 7, 12, 30, 59) in period
    assert datetime.datetime(2022, 8, 7, 12, 31, 00) not in period

def test_roll_forward_simple():
    period = Cron("30", "*", "*", "*", "*")

    # Roll tiny amount
    interv = period.rollforward(datetime.datetime(2022, 8, 7, 12, 29, 59))
    assert interv.closed == 'left'
    assert interv.left == datetime.datetime(2022, 8, 7, 12, 30, 00)
    assert interv.right == datetime.datetime(2022, 8, 7, 12, 31, 00)

    # No roll (at left)
    interv = period.rollforward(datetime.datetime(2022, 8, 7, 12, 30, 0))
    assert interv.left == datetime.datetime(2022, 8, 7, 12, 30, 00)
    assert interv.right == datetime.datetime(2022, 8, 7, 12, 31, 00)

    # No roll (at center)
    interv = period.rollforward(datetime.datetime(2022, 8, 7, 12, 30, 30))
    assert interv.left == datetime.datetime(2022, 8, 7, 12, 30, 30)
    assert interv.right == datetime.datetime(2022, 8, 7, 12, 31, 00)
    assert interv.closed == 'left'

    # No roll (at right)
    interv = period.rollforward(datetime.datetime(2022, 8, 7, 12, 30, 59, 999999))
    assert interv.left == datetime.datetime(2022, 8, 7, 12, 30, 59, 999999)
    assert interv.right == datetime.datetime(2022, 8, 7, 12, 31, 00)
    assert interv.closed == 'left'

    # Roll (at right)
    interv = period.rollforward(datetime.datetime(2022, 8, 7, 12, 31))
    assert interv.left == datetime.datetime(2022, 8, 7, 13, 30)
    assert interv.right == datetime.datetime(2022, 8, 7, 13, 31)
    assert interv.closed == 'left'

def test_roll_back_simple():
    period = Cron("30", "*", "*", "*", "*")

    # Roll tiny amount
    interv = period.rollback(datetime.datetime(2022, 8, 7, 12, 31, 1))
    assert interv.left == datetime.datetime(2022, 8, 7, 12, 30, 00)
    assert interv.right == datetime.datetime(2022, 8, 7, 12, 31, 00)
    assert interv.closed == "left"

    # No roll (at left, single point)
    interv = period.rollback(datetime.datetime(2022, 8, 7, 12, 30, 0))
    assert interv.left == datetime.datetime(2022, 8, 7, 11, 30, 00)
    assert interv.right == datetime.datetime(2022, 8, 7, 11, 31, 00)
    assert interv.closed == "left"

    # No roll (at center)
    interv = period.rollback(datetime.datetime(2022, 8, 7, 12, 30, 30))
    assert interv.left == datetime.datetime(2022, 8, 7, 12, 30, 00)
    assert interv.right == datetime.datetime(2022, 8, 7, 12, 30, 30)
    assert interv.closed == "left"

    # No roll (at right)
    interv = period.rollback(datetime.datetime(2022, 8, 7, 12, 30, 59, 999999))
    assert interv.left == datetime.datetime(2022, 8, 7, 12, 30, 00)
    assert interv.right == datetime.datetime(2022, 8, 7, 12, 30, 59, 999999)

    # Roll (at right)
    interv = period.rollback(datetime.datetime(2022, 8, 7, 14, 15))
    assert interv.left == datetime.datetime(2022, 8, 7, 13, 30)
    assert interv.right == datetime.datetime(2022, 8, 7, 13, 31)

def test_roll_minute_range():
    period = Cron("30-45", "*", "*", "*", "*")

    interv = period.rollforward(datetime.datetime.fromisoformat("2022-08-07 12:33:00"))
    assert interv.left == datetime.datetime.fromisoformat("2022-08-07 12:33:00")
    assert interv.right == datetime.datetime.fromisoformat("2022-08-07 12:34:00")

    interv = period.rollback(datetime.datetime.fromisoformat("2022-08-07 12:32:59"))
    assert interv.left == datetime.datetime.fromisoformat("2022-08-07 12:32:00")
    assert interv.right == datetime.datetime.fromisoformat("2022-08-07 12:32:59")

def test_roll_complex():
    period = Cron(*"15,30 18-22 20 OCT *".split(" "))

    interv = period.rollforward(datetime.datetime(2022, 8, 7, 10, 0, 0))
    assert interv.left == datetime.datetime.fromisoformat("2022-10-20 18:15:00")
    assert interv.right == datetime.datetime.fromisoformat("2022-10-20 18:16:00")

    interv = period.rollback(datetime.datetime(2022, 12, 7, 10, 0, 0))
    assert interv.left == datetime.datetime.fromisoformat("2022-10-20 22:30:00")
    assert interv.right == datetime.datetime.fromisoformat("2022-10-20 22:31:00")

def test_roll_conflict_day_of_week_first():
    # If day_of_month and day_of_week are passed
    # Crontab seems to prefer the one that is sooner (OR)
    period = Cron(*"15 18-22 20 OCT MON".split(" "))

    # Prefer day of week
    interv = period.rollforward(datetime.datetime(2022, 8, 7, 10, 0, 0))
    assert interv.left == datetime.datetime.fromisoformat("2022-10-03 18:15:00")
    assert interv.right == datetime.datetime.fromisoformat("2022-10-03 18:16:00")

    # Prefer day of week
    interv = period.rollback(datetime.datetime(2022, 12, 7, 10, 0, 0))
    assert interv.left == datetime.datetime.fromisoformat("2022-10-31 22:15:00")
    assert interv.right == datetime.datetime.fromisoformat("2022-10-31 22:16:00")

def test_roll_conflict_day_of_month_first():
    # If day_of_month and day_of_week are passed
    # Crontab seems to prefer the one that is sooner (OR)
    period = Cron(*"15 18-22 3 OCT FRI".split(" "))

    interv = period.rollforward(datetime.datetime(2022, 8, 7, 10, 0, 0))
    assert interv.left == datetime.datetime.fromisoformat("2022-10-03 18:15:00")
    assert interv.right == datetime.datetime.fromisoformat("2022-10-03 18:16:00")

    period = Cron(*"15 18-22 29 OCT FRI".split(" "))
    interv = period.rollback(datetime.datetime(2022, 12, 7, 10, 0, 0))
    assert interv.left == datetime.datetime.fromisoformat("2022-10-29 22:15:00")
    assert interv.right == datetime.datetime.fromisoformat("2022-10-29 22:16:00")
