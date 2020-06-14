
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
    ("2020-06-02 12:00", "2020-06-02 00:00", "2020-06-02 12:00"), 
    ("2020-06-02 00:00", "2020-06-02 00:00", "2020-06-02 00:00"),
    ("2020-06-03 23:59:59.999999", "2020-06-02 00:00", "2020-06-03 23:59:59.999999"),
    # Outside 
    ("2020-06-01 23:59:59.999999", "2020-05-26 00:00", "2020-05-27 23:59:59.999999"),
    ("2020-06-04 00:00", "2020-06-02 00:00", "2020-06-03 23:59:59.999999"),
], ids=["In interval", "In interval, left", "In interval, right", "Outside interval, left", "Outside interval, right"])
def test_prev(dt, expected_left, expected_right):
    dt = pd.Timestamp(dt)
    expected_left = pd.Timestamp(expected_left)
    expected_right = pd.Timestamp(expected_right)

    time = DaysOfWeek("Tue", "Wed")
    interval = time.prev(dt)

    assert isinstance(interval, pd.Interval)
    assert expected_left == interval.left
    assert expected_right == interval.right


@pytest.mark.parametrize("dt,expected_left,expected_right", [
    # Inside
    ("2020-06-02 12:00", "2020-06-02 12:00", "2020-06-03 23:59:59.999999"), 
    ("2020-06-02 00:00", "2020-06-02 00:00", "2020-06-03 23:59:59.999999"),
    ("2020-06-03 23:59:59.999999", "2020-06-03 23:59:59.999999", "2020-06-03 23:59:59.999999"),
    # Outside 
    ("2020-06-01 23:59:59.999999", "2020-06-02 00:00", "2020-06-03 23:59:59.999999"),
    ("2020-06-04 00:00", "2020-06-09 00:00", "2020-06-10 23:59:59.999999"),
], ids=["In interval", "In interval, left", "In interval, right", "Outside interval, left", "Outside interval, right"])
def test_next(dt, expected_left, expected_right):
    dt = pd.Timestamp(dt)
    expected_left = pd.Timestamp(expected_left)
    expected_right = pd.Timestamp(expected_right)
    
    time = DaysOfWeek("Tue", "Wed")
    interval = time.next(dt)

    assert isinstance(interval, pd.Interval)
    assert expected_left == interval.left
    assert expected_right == interval.right

# Over weekend
@pytest.mark.parametrize("dt,expected_left,expected_right", [
    # Inside
    ("2020-06-07 12:00", "2020-06-07 00:00", "2020-06-07 12:00"), 
    ("2020-06-07 00:00", "2020-06-07 00:00", "2020-06-07 00:00"),
    ("2020-06-08 23:59:59.999999", "2020-06-07 00:00", "2020-06-08 23:59:59.999999"),
    # Outside 
    ("2020-06-13 23:59:59.999999", "2020-06-07 00:00", "2020-06-08 23:59:59.999999"),
], ids=["In interval", "In interval, left", "In interval, right", "Outside interval"])
def test_prev_over_weekend(dt, expected_left, expected_right):
    dt = pd.Timestamp(dt)
    expected_left = pd.Timestamp(expected_left)
    expected_right = pd.Timestamp(expected_right)

    time = DaysOfWeek("Sun", "Mon")
    interval = time.prev(dt)

    assert isinstance(interval, pd.Interval)
    assert expected_left == interval.left
    assert expected_right == interval.right


@pytest.mark.parametrize("dt,expected_left,expected_right", [
    # Inside
    ("2020-06-07 12:00", "2020-06-07 12:00", "2020-06-08 23:59:59.999999"), 
    ("2020-06-07 00:00", "2020-06-07 00:00", "2020-06-08 23:59:59.999999"),
    ("2020-06-08 23:59:59.999999", "2020-06-08 23:59:59.999999", "2020-06-08 23:59:59.999999"),
    # Outside 
    ("2020-06-06 23:59:59.999999", "2020-06-07 00:00", "2020-06-08 23:59:59.999999"),
], ids=["In interval", "In interval, left", "In interval, right", "Outside interval"])
def test_next_over_weekend(dt, expected_left, expected_right):
    dt = pd.Timestamp(dt)
    expected_left = pd.Timestamp(expected_left)
    expected_right = pd.Timestamp(expected_right)
    
    time = DaysOfWeek("Sun", "Mon")
    interval = time.next(dt)

    assert isinstance(interval, pd.Interval)
    assert expected_left == interval.left
    assert expected_right == interval.right
