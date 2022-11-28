
from datetime import datetime, timedelta
import pytest
from rocketry.time import (
    TimeSpanDelta
)

@pytest.mark.parametrize(
    "dt,dt_ref,near,far",
    [
        # Regular
        pytest.param(
            datetime(2020, 1, 1, 10, 00),
            datetime(2020, 1, 1, 12, 00),
            "1:00:00", "2:00:00",
            id="On interval (left edge)"),
      pytest.param(
            datetime(2020, 1, 1, 11, 00),
            datetime(2020, 1, 1, 12, 00),
            "1:00:00", "2:00:00",
            id="On interval (right edge)"),
      pytest.param(
            datetime(2020, 1, 1, 10, 30),
            datetime(2020, 1, 1, 12, 00),
            "1:00:00", "2:00:00",
            id="On interval"),

        pytest.param(
            datetime(2020, 1, 1, 13, 00),
            datetime(2020, 1, 1, 12, 00),
            "1:00:00", "2:00:00",
            id="On interval (future, left edge)"),
      pytest.param(
            datetime(2020, 1, 1, 14, 00),
            datetime(2020, 1, 1, 12, 00),
            "1:00:00", "2:00:00",
            id="On interval (future, right edge)"),
      pytest.param(
            datetime(2020, 1, 1, 13, 30),
            datetime(2020, 1, 1, 12, 00),
            "1:00:00", "2:00:00",
            id="On interval (future)"),
    ],
)
def test_in_offset(dt, dt_ref, near, far):
    time = TimeSpanDelta(near, far, reference=dt_ref)
    assert time.reference is dt_ref
    assert dt in time

@pytest.mark.parametrize(
    "dt,dt_ref,near,far",
    [
        # Regular
        pytest.param(
            datetime(2020, 1, 1, 9, 59, 59, 999999),
            datetime(2020, 1, 1, 12, 00),
            "1:00:00", "2:00:00",
            id="Left from interval"),
        pytest.param(
            datetime(2020, 1, 1, 11, 00, 00, 1),
            datetime(2020, 1, 1, 12, 00),
            "1:00:00", "2:00:00",
            id="Right from interval"),
        pytest.param(
            datetime(2020, 1, 1, 12, 59, 59, 999999),
            datetime(2020, 1, 1, 12, 00),
            "1:00:00", "2:00:00",
            id="Left from interval (future)"),
        pytest.param(
            datetime(2020, 1, 1, 14, 00, 00, 1),
            datetime(2020, 1, 1, 12, 00),
            "1:00:00", "2:00:00",
            id="Right from interval (future)"),
    ],
)
def test_not_in_offset(dt, dt_ref, near, far):
    time = TimeSpanDelta(near, far, reference=dt_ref)
    #time.reference = dt_ref
    assert time.reference is dt_ref
    assert dt not in time


def test_reference_now():
    time = TimeSpanDelta(far="10 seconds").use_reference(datetime.now())
    assert datetime.now() in time
    assert (datetime.now() - timedelta(0, 5, 0)) in time
    assert (datetime.now() - timedelta(0, 11, 0)) not in time
