
from datetime import datetime


from pypipe.time.interval import (
    TimeOfHour
)

import pandas as pd
import pytest

@pytest.mark.parametrize("dt,expected_left,expected_right", [
    # Inside
    ("2020-01-01 12:35:00", "2020-01-01 12:30:00", "2020-01-01 12:35:00"), 
    ("2020-01-01 12:30:00", "2020-01-01 12:30:00", "2020-01-01 12:30:00"),
    ("2020-01-01 12:45:00", "2020-01-01 12:30:00", "2020-01-01 12:45:00"),
    # Outside 
    ("2020-01-01 12:15:00", "2020-01-01 11:30:00", "2020-01-01 11:45:00"),
    ("2020-01-01 12:50:00", "2020-01-01 12:30:00", "2020-01-01 12:45:00"),
], ids=["In interval", "In interval, left", "In interval, right", "Outside interval, left", "Outside interval, right"])
def test_rollback(dt, expected_left, expected_right):
    dt = pd.Timestamp(dt)
    expected_left = pd.Timestamp(expected_left)
    expected_right = pd.Timestamp(expected_right)

    time = TimeOfHour(30, 45)
    interval = time.rollback(dt)

    assert isinstance(interval, pd.Interval)
    assert expected_left == interval.left
    assert expected_right == interval.right


@pytest.mark.parametrize("dt,expected_left,expected_right", [
    # Inside
    ("2020-01-01 12:35:00", "2020-01-01 12:35:00", "2020-01-01 12:45:00"), 
    ("2020-01-01 12:30:00", "2020-01-01 12:30:00", "2020-01-01 12:45:00"),
    ("2020-01-01 12:45:00", "2020-01-01 12:45:00", "2020-01-01 12:45:00"),
    # Outside 
    ("2020-01-01 12:15:00", "2020-01-01 12:30:00", "2020-01-01 12:45:00"),
    ("2020-01-01 12:50:00", "2020-01-01 13:30:00", "2020-01-01 13:45:00"),
], ids=["In interval", "In interval, left", "In interval, right", "Outside interval, left", "Outside interval, right"])
def test_rollforward(dt, expected_left, expected_right):
    dt = pd.Timestamp(dt)
    expected_left = pd.Timestamp(expected_left)
    expected_right = pd.Timestamp(expected_right)
    
    time = TimeOfHour(30, 45) # 11 minutes and 00 seconds to 13 minutes and 00 seconds
    interval = time.rollforward(dt)

    assert isinstance(interval, pd.Interval)
    assert expected_left == interval.left
    assert expected_right == interval.right


# Overnight
@pytest.mark.parametrize("dt,expected_left,expected_right", [
    # Inside
    ("2020-01-01 12:50:00", "2020-01-01 12:45:00", "2020-01-01 12:50:00"), 
    ("2020-01-01 12:45:00", "2020-01-01 12:45:00", "2020-01-01 12:45:00"),
    ("2020-01-01 13:15:00", "2020-01-01 12:45:00", "2020-01-01 13:15:00"),
    # Outside 
    ("2020-01-01 12:20:00", "2020-01-01 11:45:00", "2020-01-01 12:15:00"),
    ("2020-01-01 12:40:00", "2020-01-01 11:45:00", "2020-01-01 12:15:00"), 
], ids=["In interval", "In interval, left", "In interval, right", "Outside interval, left", "Outside interval, right"])
def test_prev_overhour(dt, expected_left, expected_right):
    dt = pd.Timestamp(dt)
    expected_left = pd.Timestamp(expected_left)
    expected_right = pd.Timestamp(expected_right)

    time = TimeOfHour(45, 15)
    interval = time.rollback(dt)

    assert isinstance(interval, pd.Interval)
    assert expected_left == interval.left
    assert expected_right == interval.right

@pytest.mark.parametrize("dt,expected_left,expected_right", [
    # Inside
    ("2020-01-01 12:50:00", "2020-01-01 12:50:00", "2020-01-01 13:15:00"), 
    ("2020-01-01 12:45:00", "2020-01-01 12:45:00", "2020-01-01 13:15:00"),
    ("2020-01-01 13:15:00", "2020-01-01 13:15:00", "2020-01-01 13:15:00"),
    # Outside 
    ("2020-01-01 12:20:00", "2020-01-01 12:45:00", "2020-01-01 13:15:00"),
    ("2020-01-01 12:40:00", "2020-01-01 12:45:00", "2020-01-01 13:15:00"), 
], ids=["In interval", "In interval, left", "In interval, right", "Outside interval, left", "Outside interval, right"])
def test_next_overhour(dt, expected_left, expected_right):
    dt = pd.Timestamp(dt)
    expected_left = pd.Timestamp(expected_left)
    expected_right = pd.Timestamp(expected_right)

    time = TimeOfHour(45, 15)
    interval = time.rollforward(dt)

    assert isinstance(interval, pd.Interval)
    assert expected_left == interval.left
    assert expected_right == interval.right
