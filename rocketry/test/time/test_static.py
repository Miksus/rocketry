from datetime import datetime
from rocketry.time import StaticInterval
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