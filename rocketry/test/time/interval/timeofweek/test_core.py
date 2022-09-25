
import pytest
from rocketry.pybox.time.convert import to_datetime

from rocketry.time.interval import (
    TimeOfWeek
)

MS_IN_SECOND = 1e+6
MS_IN_MINUTE = 1e+6 * 60
MS_IN_HOUR   = 1e+6 * 60 * 60
MS_IN_DAY    = 1e+6 * 60 * 60 * 24
MS_IN_WEEK   = 1e+6 * 60 * 60 * 24 * 7

# TimeOfWeek
# Year 2024 was chosen as it starts on monday
@pytest.mark.parametrize(
    "dt,string,ms",
    [
        # Regular
        pytest.param(
            to_datetime("2024-01-01 00:00:00"),
            "Mon 00:00:00",
            0,
            id="Beginning"),
        pytest.param(
            to_datetime("2024-01-07 23:59:59.999999"),
            "Sun 23:59:59.999999",
            604799999999,
            id="Ending"),
    ],
)
def test_anchor_equal(dt, string, ms):
    time = TimeOfWeek(None, None)
    assert time.anchor_dt(dt) == time.anchor_str(string) == ms


@pytest.mark.parametrize(
    "start,end,start_ms,end_ms",
    [
        # Regular
        pytest.param(
            "Mon 00:00:00",
            "Sun 23:59:59.999999000",
            0, MS_IN_WEEK - 1,
            id="Strings: full"),
        pytest.param(
            # From Tue 00:00 to Wed 23:59:59.000 ()
            "Tue",
            "Wed", #
            MS_IN_DAY, MS_IN_DAY * 3,
            id="Strings: minimal"),
    ],
)
def test_construct(start, end, start_ms, end_ms):
    time = TimeOfWeek(start, end)
    assert time._start == start_ms
    assert time._end == end_ms
