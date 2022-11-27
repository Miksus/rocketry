
from datetime import datetime, timedelta
import pytest
from rocketry.core.time import (
    TimeDelta
)

@pytest.mark.parametrize(
    "dt,dt_ref,offset",
    [
        # Regular
        pytest.param(
            datetime(2020, 1, 1, 10, 00),
            datetime(2020, 1, 1, 12, 00),
            "2:00:00",
            id="Left of interval"),
        pytest.param(
            datetime(2020, 1, 1, 12, 00),
            datetime(2020, 1, 1, 12, 00),
            "2:00:00",
            id="Right of interval"),
        pytest.param(
            datetime(2020, 1, 1, 11, 00),
            datetime(2020, 1, 1, 12, 00),
            "2:00:00",
            id="Middle of interval"),
    ],
)
def test_in_offset(dt, dt_ref, offset):
    time = TimeDelta(offset, reference=dt_ref)
    assert dt in time

@pytest.mark.parametrize(
    "dt,dt_ref,offset",
    [
        # Regular
        pytest.param(
            datetime(2020, 1, 1, 9, 59, 59, 999999),
            datetime(2020, 1, 1, 12, 00),
            "2:00:00",
            id="Left from interval"),
        pytest.param(
            datetime(2020, 1, 1, 12, 00, 1),
            datetime(2020, 1, 1, 12, 00),
            "2:00:00",
            id="Right from interval"),
    ],
)
def test_not_in_offset(dt, dt_ref, offset):
    time = TimeDelta(offset, reference=dt_ref).use_reference(datetime.now())
    assert dt not in time


def test_reference_now():
    now = datetime.now()
    time = TimeDelta("10 seconds").use_reference(now)
    assert now in time
    assert (now - timedelta(0, 5, 0)) in time
    assert (now - timedelta(0, 11, 0)) not in time
