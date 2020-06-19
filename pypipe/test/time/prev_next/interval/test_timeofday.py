
from datetime import datetime

from pypipe.time.cycle import (
    Daily, Weekly
)
from pypipe.time.interval import (
    TimeOfDay, DaysOfWeek
)
from pypipe.time import TimeDelta

import pandas as pd
import pytest

@pytest.mark.parametrize("dt,expected_left,expected_right", [
    # Inside
    ("2020-01-01 12:00", "2020-01-01 11:00", "2020-01-01 12:00"), 
    ("2020-01-01 11:00", "2020-01-01 11:00", "2020-01-01 11:00"),
    ("2020-01-01 13:00", "2020-01-01 11:00", "2020-01-01 13:00"),
    # Outside 
    ("2020-01-01 10:00", "2019-12-31 11:00", "2019-12-31 13:00"),
    ("2020-01-01 14:00", "2020-01-01 11:00", "2020-01-01 13:00"),
], ids=["In interval", "In interval, left", "In interval, right", "Outside interval, left", "Outside interval, right"])
def test_rollback(dt, expected_left, expected_right):
    dt = pd.Timestamp(dt)
    expected_left = pd.Timestamp(expected_left)
    expected_right = pd.Timestamp(expected_right)

    time = TimeOfDay("11:00", "13:00")
    interval = time.rollback(dt)

    assert isinstance(interval, pd.Interval)
    assert expected_left == interval.left
    assert expected_right == interval.right


@pytest.mark.parametrize("dt,expected_left,expected_right", [
    # Inside
    ("2020-01-01 12:00", "2020-01-01 12:00", "2020-01-01 13:00"), 
    ("2020-01-01 11:00", "2020-01-01 11:00", "2020-01-01 13:00"),
    ("2020-01-01 13:00", "2020-01-01 13:00", "2020-01-01 13:00"),
    # Outside 
    ("2020-01-01 10:00", "2020-01-01 11:00", "2020-01-01 13:00"),
    ("2020-01-01 14:00", "2020-01-02 11:00", "2020-01-02 13:00"), 
], ids=["In interval", "In interval, left", "In interval, right", "Outside interval, left", "Outside interval, right"])
def test_rollforward(dt, expected_left, expected_right):
    dt = pd.Timestamp(dt)
    expected_left = pd.Timestamp(expected_left)
    expected_right = pd.Timestamp(expected_right)
    
    time = TimeOfDay("11:00", "13:00")
    interval = time.rollforward(dt)

    assert isinstance(interval, pd.Interval)
    assert expected_left == interval.left
    assert expected_right == interval.right


# Overnight
@pytest.mark.parametrize("dt,expected_left,expected_right", [
    # Inside
    ("2020-01-01 00:00", "2019-12-31 23:00", "2020-01-01 00:00"), 
    ("2019-12-31 23:00", "2019-12-31 23:00", "2019-12-31 23:00"),
    ("2020-01-01 01:00", "2019-12-31 23:00", "2020-01-01 01:00"),
    # Outside 
    ("2020-01-01 22:00", "2019-12-31 23:00", "2020-01-01 01:00"),
    ("2020-01-01 02:00", "2019-12-31 23:00", "2020-01-01 01:00"),
], ids=["In interval", "In interval, left", "In interval, right", "Outside interval, left", "Outside interval, right"])
def test_prev_overnight(dt, expected_left, expected_right):
    dt = pd.Timestamp(dt)
    expected_left = pd.Timestamp(expected_left)
    expected_right = pd.Timestamp(expected_right)

    time = TimeOfDay("23:00", "01:00")
    interval = time.rollback(dt)

    assert isinstance(interval, pd.Interval)
    assert expected_left == interval.left
    assert expected_right == interval.right

@pytest.mark.parametrize("dt,expected_left,expected_right", [
    # Inside
    ("2020-01-01 00:00", "2020-01-01 00:00", "2020-01-01 01:00"), 
    ("2019-12-31 23:00", "2019-12-31 23:00", "2020-01-01 01:00"),
    ("2020-01-01 01:00", "2020-01-01 01:00", "2020-01-01 01:00"),
    # Outside 
    ("2020-01-01 22:00", "2020-01-01 23:00", "2020-01-02 01:00"),
    ("2020-01-01 02:00", "2020-01-01 23:00", "2020-01-02 01:00"),
], ids=["In interval", "In interval, left", "In interval, right", "Outside interval, left", "Outside interval, right"])
def test_next_overnight(dt, expected_left, expected_right):
    dt = pd.Timestamp(dt)
    expected_left = pd.Timestamp(expected_left)
    expected_right = pd.Timestamp(expected_right)

    time = TimeOfDay("23:00", "01:00")
    interval = time.rollforward(dt)

    assert isinstance(interval, pd.Interval)
    assert expected_left == interval.left
    assert expected_right == interval.right
