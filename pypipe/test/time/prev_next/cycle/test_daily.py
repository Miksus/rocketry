
from datetime import datetime

from pypipe.time.cycle import (
    Daily, Weekly
)

import pandas as pd
import pytest

@pytest.mark.parametrize("dt,expected_left,expected_right", [
    # Inside
    ("2020-06-02 12:00", "2020-06-02 00:00", "2020-06-02 12:00"), 
    ("2020-06-02 00:00", "2020-06-02 00:00", "2020-06-02 00:00"), 
    ("2020-06-02 23:59:59.999999999", "2020-06-02 00:00", "2020-06-02 23:59:59.999999999"), 
], ids=["In interval", "In interval, left", "In interval, right"])
def test_rollback(dt, expected_left, expected_right):
    dt = pd.Timestamp(dt)
    expected_left = pd.Timestamp(expected_left)
    expected_right = pd.Timestamp(expected_right)

    time = Daily()
    interval = time.rollback(dt)

    assert isinstance(interval, pd.Interval)
    assert expected_left == interval.left
    assert expected_right == interval.right


@pytest.mark.parametrize("dt,expected_left,expected_right", [
    # Inside
    ("2020-06-02 12:00", "2020-06-02 12:00", "2020-06-02 23:59:59.999999999"), 
    ("2020-06-02 00:00", "2020-06-02 00:00", "2020-06-02 23:59:59.999999999"), 
    ("2020-06-02 23:59:59.999999999", "2020-06-02 23:59:59.999999999", "2020-06-02 23:59:59.999999999"), 
], ids=["In interval", "In interval, left", "In interval, right"])
def test_rollforward(dt, expected_left, expected_right):
    dt = pd.Timestamp(dt)
    expected_left = pd.Timestamp(expected_left)
    expected_right = pd.Timestamp(expected_right)
    
    time = Daily()
    interval = time.rollforward(dt)

    assert isinstance(interval, pd.Interval)
    assert expected_left == interval.left
    assert expected_right == interval.right


@pytest.mark.parametrize("dt,expected_left,expected_right", [
    # Inside
    ("2020-06-02 12:00", "2020-06-01 00:00", "2020-06-02 12:00"), 
    ("2020-06-02 00:00", "2020-06-01 00:00", "2020-06-02 00:00"), 
    ("2020-06-02 23:59:59.999999999", "2020-06-01 00:00", "2020-06-02 23:59:59.999999999"), 
], ids=["In interval", "In interval, left", "In interval, right"])
def test_prev_with_n(dt, expected_left, expected_right):
    dt = pd.Timestamp(dt)
    expected_left = pd.Timestamp(expected_left)
    expected_right = pd.Timestamp(expected_right)

    time = Daily(n=2)
    interval = time.rollback(dt)

    assert isinstance(interval, pd.Interval)
    assert expected_left == interval.left
    assert expected_right == interval.right


@pytest.mark.parametrize("dt,expected_left,expected_right", [
    # Inside
    ("2020-06-02 12:00", "2020-06-02 12:00", "2020-06-03 23:59:59.999999999"), 
    ("2020-06-02 00:00", "2020-06-02 00:00", "2020-06-03 23:59:59.999999999"), 
    ("2020-06-02 23:59:59.999999999", "2020-06-02 23:59:59.999999999", "2020-06-03 23:59:59.999999999"), 
], ids=["In interval", "In interval, left", "In interval, right"])
def test_next_with_n(dt, expected_left, expected_right):
    dt = pd.Timestamp(dt)
    expected_left = pd.Timestamp(expected_left)
    expected_right = pd.Timestamp(expected_right)
    
    time = Daily(n=2)
    interval = time.rollforward(dt)

    assert isinstance(interval, pd.Interval)
    assert expected_left == interval.left
    assert expected_right == interval.right