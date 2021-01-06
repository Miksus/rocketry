
from datetime import datetime

from pypipe.time.interval import (
    TimeOfDay, DaysOfWeek
)
from pypipe.time import TimeDelta

import pandas as pd
import pytest

@pytest.mark.parametrize("start,end", [
    # Inside
    ("Tue", "Thu"), 
    ("Tuesday", "Thursday"), 
    (1, 3), 
], ids=["Week day abbr", "Week day names", "Week day num"])
def test_construct_range(start, end):
    time = DaysOfWeek(start=start, end=end)
    mask = time.offset.weekmask
    assert [0, 1, 1, 1, 0, 0, 0] == mask

@pytest.mark.parametrize("start,end", [
    # Inside
    ("Tue", "Thu"), 
    ("Tuesday", "Thursday"), 
    (1, 3), 
], ids=["Week day abbr", "Week day names", "Week day num"])
def test_construct_values(start, end):
    time = DaysOfWeek(start, end)
    mask = time.offset.weekmask
    assert [0, 1, 0, 1, 0, 0, 0] == mask


# individual days
@pytest.mark.parametrize("dt,expected_left,expected_right", [
    # Inside
    ("2020-09-22 12:00", "2020-09-22 00:00", "2020-09-22 12:00"), 
    ("2020-09-24 00:00", "2020-09-24 00:00", "2020-09-24 00:00"),
    ("2020-09-22 23:59:59.999999", "2020-09-22 00:00", "2020-09-22 23:59:59.999999"),
    # Outside 
    ("2020-09-21 12:00", "2020-09-17 00:00", "2020-09-17 23:59:59.999999"),
    ("2020-09-23 12:00", "2020-09-22 00:00", "2020-09-22 23:59:59.999999"),
    ("2020-09-25 12:00", "2020-09-24 00:00", "2020-09-24 23:59:59.999999"),
], ids=["In interval", "In interval, left", "In interval, right", "Outside interval, left", "Outside interval, center", "Outside interval, right"])
def test_rollback_values(dt, expected_left, expected_right):
    dt = pd.Timestamp(dt)
    expected_left = pd.Timestamp(expected_left)
    expected_right = pd.Timestamp(expected_right)

    time = DaysOfWeek("Tue", "Thu")
    interval = time.rollback(dt)

    assert isinstance(interval, pd.Interval)
    assert expected_left == interval.left
    assert expected_right == interval.right

@pytest.mark.parametrize("dt,expected_left,expected_right", [
    # Inside
    ("2020-09-22 12:00", "2020-09-22 12:00", "2020-09-22 23:59:59.999999"), 
    ("2020-09-24 00:00", "2020-09-24 00:00", "2020-09-24 23:59:59.999999"),
    ("2020-09-24 23:59:59.999999", "2020-09-24 23:59:59.999999", "2020-09-24 23:59:59.999999"),
    # Outside 
    ("2020-09-21 12:00", "2020-09-22 00:00", "2020-09-22 23:59:59.999999"),
    ("2020-09-23 12:00", "2020-09-24 00:00", "2020-09-24 23:59:59.999999"),
    ("2020-09-25 00:00", "2020-09-29 00:00", "2020-09-29 23:59:59.999999"),
], ids=["In interval", "In interval, left", "In interval, right", "Outside interval, left", "Outside interval, center", "Outside interval, right"])
def test_rollforward_values(dt, expected_left, expected_right):
    dt = pd.Timestamp(dt)
    expected_left = pd.Timestamp(expected_left)
    expected_right = pd.Timestamp(expected_right)
    
    time = DaysOfWeek("Tue", "Thu")
    interval = time.rollforward(dt)

    assert isinstance(interval, pd.Interval)
    assert expected_left == interval.left
    assert expected_right == interval.right


# Range
@pytest.mark.parametrize("dt,expected_left,expected_right", [
    # Inside
    ("2020-09-23 12:00", "2020-09-22 00:00", "2020-09-23 12:00"), 
    ("2020-09-22 00:00", "2020-09-22 00:00", "2020-09-22 00:00"),
    ("2020-09-24 23:59:59.999999", "2020-09-22 00:00", "2020-09-24 23:59:59.999999"),
    # Outside 
    ("2020-09-21 12:00", "2020-09-15 00:00", "2020-09-17 23:59:59.999999"),
    ("2020-09-25 12:00", "2020-09-22 00:00", "2020-09-24 23:59:59.999999"),
], ids=["In interval", "In interval, left", "In interval, right", "Outside interval, left", "Outside interval, right"])
def test_rollback_range(dt, expected_left, expected_right):
    dt = pd.Timestamp(dt)
    expected_left = pd.Timestamp(expected_left)
    expected_right = pd.Timestamp(expected_right)

    time = DaysOfWeek(start="Tue", end="Thu")
    interval = time.rollback(dt)

    assert isinstance(interval, pd.Interval)
    assert expected_left == interval.left
    assert expected_right == interval.right

@pytest.mark.parametrize("dt,expected_left,expected_right", [
    # Inside
    ("2020-09-23 12:00", "2020-09-23 12:00", "2020-09-24 23:59:59.999999"), 
    ("2020-09-22 00:00", "2020-09-22 00:00", "2020-09-24 23:59:59.999999"),
    ("2020-09-24 23:59:59.999999", "2020-09-24 23:59:59.999999", "2020-09-24 23:59:59.999999"),
    # Outside 
    ("2020-09-21 12:00", "2020-09-22 00:00", "2020-09-24 23:59:59.999999"),
    ("2020-09-25 12:00", "2020-09-29 00:00", "2020-10-01 23:59:59.999999"),
], ids=["In interval", "In interval, left", "In interval, right", "Outside interval, left", "Outside interval, right"])
def test_rollforward_range(dt, expected_left, expected_right):
    dt = pd.Timestamp(dt)
    expected_left = pd.Timestamp(expected_left)
    expected_right = pd.Timestamp(expected_right)
    
    time = DaysOfWeek(start="Tue", end="Thu")
    interval = time.rollforward(dt)

    assert isinstance(interval, pd.Interval)
    assert expected_left == interval.left
    assert expected_right == interval.right



# Original
@pytest.mark.parametrize("dt,expected_left,expected_right", [
    # Inside
    ("2020-06-02 12:00", "2020-06-02 00:00", "2020-06-02 12:00"), 
    ("2020-06-02 00:00", "2020-06-02 00:00", "2020-06-02 00:00"),
    ("2020-06-03 23:59:59.999999", "2020-06-02 00:00", "2020-06-03 23:59:59.999999"),
    # Outside 
    ("2020-06-01 23:59:59.999999", "2020-05-26 00:00", "2020-05-27 23:59:59.999999"),
    ("2020-06-04 00:00", "2020-06-02 00:00", "2020-06-03 23:59:59.999999"),
], ids=["In interval", "In interval, left", "In interval, right", "Outside interval, left", "Outside interval, right"])
def test_rollback(dt, expected_left, expected_right):
    dt = pd.Timestamp(dt)
    expected_left = pd.Timestamp(expected_left)
    expected_right = pd.Timestamp(expected_right)

    time = DaysOfWeek("Tue", "Wed")
    interval = time.rollback(dt)

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
def test_rollforward(dt, expected_left, expected_right):
    dt = pd.Timestamp(dt)
    expected_left = pd.Timestamp(expected_left)
    expected_right = pd.Timestamp(expected_right)
    
    time = DaysOfWeek("Tue", "Wed")
    interval = time.rollforward(dt)

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
    interval = time.rollback(dt)

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
    interval = time.rollforward(dt)

    assert isinstance(interval, pd.Interval)
    assert expected_left == interval.left
    assert expected_right == interval.right
