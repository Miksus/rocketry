from datetime import datetime
import pytest
from rocketry.pybox.time import Interval, to_datetime

@pytest.mark.parametrize("l,r",
    [
        pytest.param(
            Interval(to_datetime("2022-07-01"), to_datetime("2022-07-30")),
            Interval(to_datetime("2022-07-12"), to_datetime("2022-07-15")),
            id="right inside left"
        ),
        pytest.param(
            Interval(to_datetime("2022-07-12"), to_datetime("2022-07-15")),
            Interval(to_datetime("2022-07-01"), to_datetime("2022-07-30")),
            id="left inside right"
        ),

        pytest.param(
            Interval(to_datetime("2022-07-01"), to_datetime("2022-07-15"), closed="neither"),
            Interval(to_datetime("2022-07-14"), to_datetime("2022-07-30"), closed="neither"),
            id="left partially right (right)"
        ),
        pytest.param(
            Interval(to_datetime("2022-07-14"), to_datetime("2022-07-30"), closed="neither"),
            Interval(to_datetime("2022-07-01"), to_datetime("2022-07-15"), closed="neither"),
            id="left partially right (left)"
        ),

        pytest.param(
            Interval(to_datetime("2022-07-01"), to_datetime("2022-07-12"), closed="both"),
            Interval(to_datetime("2022-07-12"), to_datetime("2022-07-15"), closed="both"),
            id="left edges right (right)"
        ),
        pytest.param(
            Interval(to_datetime("2022-07-12"), to_datetime("2022-07-15"), closed="both"),
            Interval(to_datetime("2022-07-01"), to_datetime("2022-07-12"), closed="both"),
            id="left edges right (left)"
        ),
    ]
)
def test_overlaps(l, r):
    assert l.overlaps(r)


@pytest.mark.parametrize("l,r",
    [
        pytest.param(
            Interval(to_datetime("2022-07-01"), to_datetime("2022-07-12"), closed=l_closed),
            Interval(to_datetime("2022-07-12"), to_datetime("2022-07-30"), closed=r_closed),
            id=f"right edge ({l_closed}, {r_closed})"
        )
        for l_closed, r_closed in [
            ("left", 'left'), ('left', 'both'), ('left', 'neither'),
            ("left", 'right'), ('both', 'right'), ('neither', 'right'),
            ("neither", 'both'), ('neither', 'neither'),
        ]
    ]
)
def test_not_overlaps(l, r):
    assert not l.overlaps(r)

def test_fail():
    with pytest.raises(ValueError):
        Interval(datetime(2022, 1, 1), datetime(2019, 1, 1))
    with pytest.raises(ValueError):
        Interval(datetime(2022, 1, 1), datetime(2022, 1, 2), closed="typo")

def test_empty():
    assert not Interval(datetime(2022, 1, 1), datetime(2022, 1, 1), closed="both").is_empty
    for closed in ("left", "right", "both", "neither"):
        assert not Interval(datetime(2022, 1, 1), datetime(2022, 1, 2), closed=closed).is_empty
    for closed in ("left", "right", "neither"):
        assert Interval(datetime(2022, 1, 1), datetime(2022, 1, 1), closed=closed).is_empty

def test_repr():
    for closed in ("left", "right", "neither"):
        assert repr(Interval(datetime(2022, 1, 1), datetime(2022, 1, 1), closed=closed))
