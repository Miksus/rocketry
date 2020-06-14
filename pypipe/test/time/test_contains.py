
from datetime import datetime

from pypipe.time.cycle import (
    Daily, Weekly
)
from pypipe.time.interval import (
    TimeOfDay, DaysOfWeek
)
from pypipe.time import TimeDelta

import pytest

@pytest.mark.parametrize("dt", [datetime(2020, 6, 1, 12, 0), datetime(2020, 6, 1, 11, 0),datetime(2020, 6, 1, 13, 0)])
def test_timeofday_true(dt):
    time = TimeOfDay("11:00", "13:00")
    assert dt in time

@pytest.mark.parametrize("dt", [datetime(2020, 6, 1, 13, 0, 1), datetime(2020, 6, 1, 10, 0, 59)])
def test_timeofday_false(dt):
    time = TimeOfDay("11:00", "13:00")
    assert dt not in time

@pytest.mark.parametrize("dt", [datetime(2020, 6, 1, 23, 0), datetime(2020, 6, 1, 2, 0), datetime(2020, 6, 1, 5, 0)])
def test_timeofday_overnight_true(dt):
    time = TimeOfDay("23:00", "05:00")
    assert dt in time

@pytest.mark.parametrize("dt", [datetime(2020, 6, 1, 22, 59), datetime(2020, 6, 2, 5, 0, 0, 1), datetime(2020, 6, 1, 12, 0)])
def test_timeofday_overnight_false(dt):
    time = TimeOfDay("23:00", "05:00")
    assert dt not in time



@pytest.mark.parametrize("dt", [datetime(2020, 6, 1, 0, 0), datetime(2020, 6, 5, 23, 59)])
def test_daysofweek_true(dt):
    time = DaysOfWeek("Mon", "Fri")
    assert dt in time

@pytest.mark.parametrize("dt", [datetime(2020, 6, 2, 0, 0), datetime(2020, 6, 4, 23, 59)])
def test_daysofweek_false(dt):
    time = DaysOfWeek("Mon", "Fri")
    assert dt not in time

