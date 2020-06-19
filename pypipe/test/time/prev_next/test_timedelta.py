

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
    ("2020-06-02 12:00", "2020-06-01 10:00", "2020-06-02 12:00"), 
], ids=["In interval"])
def test_rollback(dt, expected_left, expected_right):
    dt = pd.Timestamp(dt)
    expected_left = pd.Timestamp(expected_left)
    expected_right = pd.Timestamp(expected_right)

    time = TimeDelta("1 days 2 hours")
    interval = time.rollback(dt)

    assert isinstance(interval, pd.Interval)
    assert expected_left == interval.left
    assert expected_right == interval.right


@pytest.mark.parametrize("dt,expected_left,expected_right", [
    # Inside
    ("2020-06-02 12:00", "2020-06-02 12:00", "2020-06-03 14:00"), 
], ids=["In interval"])
def test_rollforward(dt, expected_left, expected_right):
    dt = pd.Timestamp(dt)
    expected_left = pd.Timestamp(expected_left)
    expected_right = pd.Timestamp(expected_right)

    time = TimeDelta("1 days 2 hours")
    interval = time.rollforward(dt)

    assert isinstance(interval, pd.Interval)
    assert expected_left == interval.left
    assert expected_right == interval.right
