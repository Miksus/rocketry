from datetime import datetime
from rocketry.time import StaticInterval, always, never
from rocketry.pybox.time import Interval

def test_static():
    t = StaticInterval("2022-08-01", "2022-08-10")
    assert datetime.fromisoformat("2022-07-31 23:59:59") not in t
    assert datetime.fromisoformat("2022-08-01 00:00:00") in t
    assert datetime.fromisoformat("2022-08-09 12:59:00") in t
    assert datetime.fromisoformat("2022-08-10 00:00:00") not in t

    assert t.rollforward("2022-07-01 00:00:00") == Interval(
        datetime.fromisoformat("2022-08-01 00:00:00"),
        datetime.fromisoformat("2022-08-10 00:00:00"),
        closed="left"
    )
    assert t.rollback("2022-09-01 00:00:00") == Interval(
        datetime.fromisoformat("2022-08-01 00:00:00"),
        datetime.fromisoformat("2022-08-10 00:00:00"),
        closed="left"
    )
    assert t.rollforward("2022-09-01 00:00:00") == Interval(
        datetime.fromisoformat("2260-01-01 00:00:00"),
        datetime.fromisoformat("2260-01-01 00:00:00"),
        closed="left"
    )

    assert t.rollforward("2022-08-03 00:00:00") == Interval(
        datetime.fromisoformat("2022-08-03 00:00:00"),
        datetime.fromisoformat("2022-08-10 00:00:00"),
        closed="left"
    )
    assert t.rollback("2022-08-03 00:00:00") == Interval(
        datetime.fromisoformat("2022-08-01 00:00:00"),
        datetime.fromisoformat("2022-08-03 00:00:00"),
        closed="left"
    )

def test_always():
    assert datetime(2022, 1, 1) in always
    assert always.rollforward(datetime(2022, 1, 1)) == Interval(
        datetime(2022, 1, 1, 0, 0),
        datetime(2260, 1, 1, 0, 0),
        closed='left'
    )
    assert always.rollback(datetime(2022, 1, 1)) == Interval(
        datetime(1970, 1, 3, 2, 0),
        datetime(2022, 1, 1, 0, 0),
        closed='left'
    )
    assert always.is_max_interval

def test_never():
    assert datetime(2022, 1, 1) not in never
    assert never.rollforward(datetime(2022, 1, 1)) == Interval(
        datetime(2260, 1, 1, 0, 0),
        datetime(2260, 1, 1, 0, 0),
        closed='left'
    )
    assert never.rollback(datetime(2022, 1, 1)) == Interval(
        datetime(1970, 1, 3, 2, 0),
        datetime(1970, 1, 3, 2, 0),
        closed='left'
    )
    assert not never.is_max_interval
