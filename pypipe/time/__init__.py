# Imports
from .base import (
    TimePeriod, TimeInterval, 
    TimeDelta, TimeCycle,
    StaticInterval,
    All, Any,
    register_class
)
from .cycle import (
    
    Hourly, Quarterly, Minutely,
    Daily, Weekly
)
from .interval import (
    TimeOfMinute,
    TimeOfHour,
    TimeOfDay,
    DaysOfWeek,
    #weekend, 
    #month_end,
    #month_begin,
    OffsetInterval
)

from .factory import period_factory

# Syntax
import pandas as pd
import calendar

# Cycle
minutely = Minutely()
daily = Daily()
# today = Daily()
# yesterday = Daily(n=2)
weekly = Weekly()

# Interval
weekend = DaysOfWeek("Sat", "Sun")
weekday = DaysOfWeek("Mon", "Tue", "Wed", "Thu", "Fri")

month_end = OffsetInterval(pd.offsets.MonthEnd())
month_begin = OffsetInterval(pd.offsets.MonthBegin())



minutely.register("minutely", group="in_")
weekend.register("weekend", group="in_")
weekday.register("weekday", group="in_")
# Register all week days
for weekday in (*calendar.day_name, *calendar.day_abbr):
    DaysOfWeek(weekday).register(weekday, group="in_")

# Register classes
for cls in (
    Weekly, Daily, Hourly, Quarterly, Minutely,
    TimeOfDay, DaysOfWeek
    ):
    register_class(cls)

del pd
del calendar