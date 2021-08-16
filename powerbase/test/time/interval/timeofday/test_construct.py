

from powerbase.time.interval import (
    TimeOfDay
)

import pytest

NS_IN_SECOND = 1e+9
NS_IN_MINUTE = 1e+9 * 60
NS_IN_HOUR   = 1e+9 * 60 * 60

@pytest.mark.parametrize(
    "start,end,start_ns,end_ns",
    [
        pytest.param(
            "10:00", "12:00",
            10 * NS_IN_HOUR, 
            12 * NS_IN_HOUR,
            id="Strings"),
        pytest.param(
            "10:20:30", "12:20:30",
            10 * NS_IN_HOUR + 20 * NS_IN_MINUTE + 30 * NS_IN_SECOND, 
            12 * NS_IN_HOUR + 20 * NS_IN_MINUTE + 30 * NS_IN_SECOND,
            id="Strings Accurate"),
        pytest.param(
            10, 12,
            10 * NS_IN_HOUR, 
            12 * NS_IN_HOUR,
            id="Integers", marks=pytest.mark.xfail(reason="Requires thinking")),

        # Open
        pytest.param(
            "10:00", None,
            10 * NS_IN_HOUR, 
            24 * NS_IN_HOUR,
            id="Right Open"),
        pytest.param(
            None, "12:00",
            0, 
            12 * NS_IN_HOUR,
            id="Left Open"),
        pytest.param(
            None, None,
            0, 
            24 * NS_IN_HOUR,
            id="Full Open"),
    ],
)
def test_construct(start, end, start_ns, end_ns):
    time = TimeOfDay(start, end)
    assert start_ns == time._start
    assert end_ns == time._end
