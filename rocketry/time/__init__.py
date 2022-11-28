from rocketry.core.time import (All, Any, StaticInterval, TimeDelta, always,
                                never)
from rocketry.session import Session

from .construct import (get_after, get_before, get_between, get_full_cycle,
                        get_on)
from .cron import Cron
from .delta import TimeSpanDelta
from .interval import *

Session._time_parsers.update(
    {
        re.compile(r"time of (?P<type_>month|week|day|hour|minute) between (?P<start>.+) and (?P<end>.+)"): get_between,
        re.compile(r"time of (?P<type_>month|week|day|hour|minute) after (?P<start>.+)"): get_after,
        re.compile(r"time of (?P<type_>month|week|day|hour|minute) before (?P<end>.+)"): get_before,
        re.compile(r"time of (?P<type_>month|week) on (?P<start>.+)"): get_on,

        re.compile(r"every (?P<past>.+)"): TimeDelta,
        re.compile(r"past (?P<past>.+)"): TimeDelta,
        "always": always,
        "never": never,
    }
)
