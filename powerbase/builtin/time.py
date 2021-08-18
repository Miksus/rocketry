
from powerbase.parse._time.time_item import add_time_parser

from powerbase.time import (
    TimeOfWeek,
    TimeOfDay,
    TimeOfHour,
    TimeOfMinute,
    TimeDelta,
)
from .period_utils import get_between, get_after, get_before

for regex, func in [
    (r"time of (?P<type_>month|week|day|hour|minute) between (?P<start>.+) and (?P<end>.+)", lambda **kwargs: get_between(**kwargs)),
    (r"time of (?P<type_>month|week|day|hour|minute) after (?P<start>.+)",                   lambda **kwargs: get_after(**kwargs)),
    (r"time of (?P<type_>month|week|day|hour|minute) before (?P<end>.+)",                    lambda **kwargs: get_before(**kwargs)),
]:
    add_time_parser(regex, func, regex=True)