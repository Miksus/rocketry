from pypipe.time import TimeInterval, TimeDelta, TimeCycle, TimePeriod

from pypipe.time import TimeOfDay, DaysOfWeek, period_factory

import datetime

def test_factory_between_timeofday():
    # Actual test
    time = period_factory.between("10:00", "11:00")

    assert isinstance(time, TimeOfDay)

def test_factory_between_daysofweek():
    # Actual test
    time = period_factory.between("Mon", "Fri")

    assert isinstance(time, DaysOfWeek)

def test_factory_past():
    # Actual test
    time = period_factory.past("1 days")

    assert isinstance(time, TimeDelta)

def test_factory_from():
    # Actual test
    time = period_factory.from_("Mon")

    assert isinstance(time, TimeCycle)