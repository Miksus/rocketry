from pypipe.conditions import IsTimeOfDay

import datetime

def test_condition_true():
    now = datetime.datetime.combine(
        datetime.date(2020, 1, 1),
        datetime.time(10, 00)
    )
    
    # Setting "current_datetime" artificially
    IsTimeOfDay.mode = "test"
    IsTimeOfDay.set_current_datetime(now)

    # Actual test
    cond = IsTimeOfDay("09:00", "12:00")

    assert bool(cond)

def test_condition_true_over_night():
    now = datetime.datetime.combine(
        datetime.date(2020, 1, 1),
        datetime.time(2, 00)
    )
    
    # Setting "current_datetime" artificially
    IsTimeOfDay.mode = "test"
    IsTimeOfDay.set_current_datetime(now)

    # Actual test
    cond = IsTimeOfDay("22:00", "05:00") # 22:00 --> 05:00 (next day)

    assert bool(cond)

def test_condition_false_before():
    now = datetime.datetime.combine(
        datetime.date(2020, 1, 1),
        datetime.time(10, 00)
    )
    
    # Setting "current_datetime" artificially
    IsTimeOfDay.mode = "test"
    IsTimeOfDay.set_current_datetime(now)

    # Actual test
    cond = IsTimeOfDay("11:00", "12:00")

    assert not bool(cond)

def test_condition_false_after():
    now = datetime.datetime.combine(
        datetime.date(2020, 1, 1),
        datetime.time(13, 00)
    )
    
    # Setting "current_datetime" artificially
    IsTimeOfDay.mode = "test"
    IsTimeOfDay.set_current_datetime(now)

    # Actual test
    cond = IsTimeOfDay("11:00", "12:00")

    assert not bool(cond)

def test_condition_false_over_night_before():
    now = datetime.datetime.combine(
        datetime.date(2020, 1, 1),
        datetime.time(21, 00)
    )
    
    # Setting "current_datetime" artificially
    IsTimeOfDay.mode = "test"
    IsTimeOfDay.set_current_datetime(now)

    # Actual test
    cond = IsTimeOfDay("22:00", "05:00")

    assert not bool(cond)

def test_condition_false_over_night_after():
    now = datetime.datetime.combine(
        datetime.date(2020, 1, 1),
        datetime.time(6, 00)
    )
    
    # Setting "current_datetime" artificially
    IsTimeOfDay.mode = "test"
    IsTimeOfDay.set_current_datetime(now)

    # Actual test
    cond = IsTimeOfDay("22:00", "05:00")

    assert not bool(cond)