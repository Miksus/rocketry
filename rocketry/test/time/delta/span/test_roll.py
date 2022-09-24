
import pytest
from rocketry.time import (
    TimeSpanDelta
)
from rocketry.pybox.time.convert import to_datetime

@pytest.mark.parametrize(
    "dt,near,far,roll_start,roll_end",
    [
        pytest.param(
            to_datetime("2020-01-01 10:00:00"),
            "1:00:00", "1:20:30",
            to_datetime("2020-01-01 11:00:00"), to_datetime("2020-01-01 11:20:30"),
            id="Closed"),
        pytest.param(
            to_datetime("2020-01-01 10:00:00"),
            "1:00:00", None,
            to_datetime("2020-01-01 11:00:00"), TimeSpanDelta.max,
            id="Open right"),
        pytest.param(
            to_datetime("2020-01-01 10:00:00"),
            None, "1:20:30",
            to_datetime("2020-01-01 10:00:00"), to_datetime("2020-01-01 11:20:30"),
            id="Open left"),
    ],
)
def test_rollforward(dt, near, far, roll_start, roll_end):
    time = TimeSpanDelta(near, far)

    interval = time.rollforward(dt)
    assert roll_start == interval.left
    assert roll_end == interval.right


@pytest.mark.parametrize(
    "dt,near,far,roll_start,roll_end",
    [
        pytest.param(
            to_datetime("2020-01-01 10:00:00"),
            "1:00:00", "1:20:30",
            to_datetime("2020-01-01 08:39:30"), to_datetime("2020-01-01 09:00:00"),
            id="Closed"),
        pytest.param(
            to_datetime("2020-01-01 10:00:00"),
            "1:20:30", None,
            TimeSpanDelta.min, to_datetime("2020-01-01 08:39:30"),
            id="Open right"),
        pytest.param(
            to_datetime("2020-01-01 10:00:00"),
            None, "1:20:30",
            to_datetime("2020-01-01 08:39:30"), to_datetime("2020-01-01 10:00:00"),
            id="Open left"),
    ],
)
def test_rollback(dt, near, far, roll_start, roll_end):
    time = TimeSpanDelta(near, far)

    interval = time.rollback(dt)
    assert roll_start == interval.left
    assert roll_end == interval.right
