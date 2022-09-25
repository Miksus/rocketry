import datetime
import pytest
from rocketry.time import RelativeDay

@pytest.mark.parametrize("day,left,right", [
    pytest.param('today', datetime.datetime(2022, 5, 15), datetime.datetime(2022, 5, 15, 23, 59, 59, 999999)),
])
def test_rollback(day, left, right):
    rel_day = RelativeDay(day)

    dt = datetime.datetime(2022, 5, 15)
    interval = rel_day.rollback(dt)
    assert interval.left == left
    assert interval.right == right


def test_rollforward():
    rel_day = RelativeDay("today")
    with pytest.raises(AttributeError):
        interval = rel_day.rollforward(datetime.datetime(2022, 5, 15))


def test_repr():
    rel_day = RelativeDay("today")
    repr(rel_day)
