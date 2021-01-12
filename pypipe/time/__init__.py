from .interval import *
from pypipe.core.time import TimeDelta

# Syntax
import pandas as pd
import calendar

# # Cycle
# minutely = Minutely()
# daily = Daily()
# # today = Daily()
# # yesterday = Daily(n=2)
# weekly = Weekly()
# 
# # Interval
# weekend = DaysOfWeek("Sat", "Sun")
# weekday = DaysOfWeek("Mon", "Tue", "Wed", "Thu", "Fri")
# 
# month_end = OffsetInterval(pd.offsets.MonthEnd())
# month_begin = OffsetInterval(pd.offsets.MonthBegin())
# 
# 
# 
# minutely.register("minutely", group="in_")
# weekend.register("weekend", group="in_")
# weekday.register("weekday", group="in_")
# # Register all week days
# for weekday in (*calendar.day_name, *calendar.day_abbr):
#     DaysOfWeek(weekday).register(weekday, group="in_")
# 
# # Register classes
# for cls in (
#     Weekly, Daily, Hourly, Minutely, # , Quarterly
#     TimeOfDay, DaysOfWeek
#     ):
#     register_class(cls)
# 
# del pd
# del calendar