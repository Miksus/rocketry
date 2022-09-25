import pytest

from rocketry.time import Any
from rocketry.time import TimeOfDay, TimeOfHour, TimeOfWeek
from rocketry.time.interval import TimeOfMinute, TimeOfMonth, TimeOfYear

def test_time_of_day_every_second():
    every_second_hour = TimeOfDay.create_range(step=2)
    assert isinstance(every_second_hour, Any)
    assert len(every_second_hour.periods) == 12
    assert every_second_hour == Any(
        TimeOfDay("00:00", "01:00"),
        #TimeOfDay("01:00", "02:00"),
        TimeOfDay("02:00", "03:00"),
        #TimeOfDay("03:00", "04:00"),
        TimeOfDay("04:00", "05:00"),
        #TimeOfDay("05:00", "06:00"),
        TimeOfDay("06:00", "07:00"),
        #TimeOfDay("07:00", "08:00"),
        TimeOfDay("08:00", "09:00"),
        #TimeOfDay("09:00", "10:00"),
        TimeOfDay("10:00", "11:00"),
        #TimeOfDay("11:00", "12:00"),
        TimeOfDay("12:00", "13:00"),
        #TimeOfDay("13:00", "14:00"),
        TimeOfDay("14:00", "15:00"),
        #TimeOfDay("15:00", "16:00"),
        TimeOfDay("16:00", "17:00"),
        #TimeOfDay("17:00", "18:00"),
        TimeOfDay("18:00", "19:00"),
        #TimeOfDay("19:00", "20:00"),
        TimeOfDay("20:00", "21:00"),
        #TimeOfDay("21:00", "22:00"),
        TimeOfDay("22:00", "23:00"),
        #TimeOfDay("23:00", "24:00"),
    )

def test_time_of_day_every_third():
    every_second_hour = TimeOfDay.create_range(step=3)
    assert isinstance(every_second_hour, Any)
    assert every_second_hour == Any(
        TimeOfDay("00:00", "01:00"),
        #TimeOfDay("01:00", "02:00"),
        #TimeOfDay("02:00", "03:00"),
        TimeOfDay("03:00", "04:00"),
        #TimeOfDay("04:00", "05:00"),
        #TimeOfDay("05:00", "06:00"),
        TimeOfDay("06:00", "07:00"),
        #TimeOfDay("07:00", "08:00"),
        #TimeOfDay("08:00", "09:00"),
        TimeOfDay("09:00", "10:00"),
        #TimeOfDay("10:00", "11:00"),
        #TimeOfDay("11:00", "12:00"),
        TimeOfDay("12:00", "13:00"),
        #TimeOfDay("13:00", "14:00"),
        #TimeOfDay("14:00", "15:00"),
        TimeOfDay("15:00", "16:00"),
        #TimeOfDay("16:00", "17:00"),
        #TimeOfDay("17:00", "18:00"),
        TimeOfDay("18:00", "19:00"),
        #TimeOfDay("19:00", "20:00"),
        #TimeOfDay("20:00", "21:00"),
        TimeOfDay("21:00", "22:00"),
        #TimeOfDay("22:00", "23:00"),
        #TimeOfDay("23:00", "24:00"),
    )

@pytest.mark.parametrize("cls,step,n_periods",
    [
        pytest.param(TimeOfMinute, 1, 60, id="TimeOfMinute (every second)"),
        pytest.param(TimeOfHour, 1, 60, id="TimeOfHour (every minute)"),
        pytest.param(TimeOfDay, 1, 24, id="TimeOfDay (every hour)"),
        pytest.param(TimeOfWeek, 1, 7, id="TimeOfWeek (every day of week)"),
        pytest.param(TimeOfMonth, 1, 31, id="TimeOfMonth (every day of month)"),
        pytest.param(TimeOfYear, 1, 12, id="TimeOfYear (every month)"),

        pytest.param(TimeOfMinute, 2, 30, id="TimeOfMinute (every second second)"),
        pytest.param(TimeOfHour, 2, 30, id="TimeOfHour (every second minute)"),
        pytest.param(TimeOfDay, 2, 12, id="TimeOfDay (every second hour)"),
        pytest.param(TimeOfWeek, 2, 4, id="TimeOfWeek (every second day of week)"),
        pytest.param(TimeOfMonth, 2, 16, id="TimeOfMonth (every second day of month)"),
        pytest.param(TimeOfYear, 2, 6, id="TimeOfYear (every second month)"),

        pytest.param(TimeOfMinute, 3, 20, id="TimeOfMinute (every third second)"),
        pytest.param(TimeOfHour, 3, 20, id="TimeOfHour (every third minute)"),
        pytest.param(TimeOfDay, 3, 8, id="TimeOfDay (every third hour)"),
        pytest.param(TimeOfWeek, 3, 3, id="TimeOfWeek (every third day of week)"),
        pytest.param(TimeOfMonth, 3, 11, id="TimeOfMonth (every third day of month)"),
        pytest.param(TimeOfYear, 3, 4, id="TimeOfYear (every third month)"),

        pytest.param(TimeOfMinute, 61, 1, id="TimeOfMinute (over the period)"),
        pytest.param(TimeOfHour, 61, 1, id="TimeOfHour (over the period)"),
        pytest.param(TimeOfDay, 24, 1, id="TimeOfDay (over the period)"),
        pytest.param(TimeOfWeek, 7, 1, id="TimeOfWeek (over the period)"),
        pytest.param(TimeOfMonth, 31, 1, id="TimeOfMonth (over the period)"),
        pytest.param(TimeOfYear, 12, 1, id="TimeOfYear (over the period)"),
    ]
)
def test_every_second(cls, step, n_periods):
    every = cls.create_range(step=step)
    assert isinstance(every, Any)
    assert len(every.periods) == n_periods
