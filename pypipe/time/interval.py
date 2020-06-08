
import datetime
import calendar

from .base import TimeInterval

from .utils import floor_time, ceil_time

import pandas as pd


# Pandas
class OffsetInterval(TimeInterval):
    """Base for interval constructed from pandas.offsets
    """
    def __init__(self, offset):
        self.offset = offset

    def __contains__(self, dt):
        # is_on_offset may return np.bool_ type which
        # acts a bit differently than Python bool
        # thus forced to bool
        return bool(self.offset.is_on_offset(dt))

    def rollforward(self, dt):
        "Roll forward till the next start datetime (if not already)"
        return self.offset.rollforward(dt)

    def rollback(self, dt):
        return self.offset.rollback(dt)

    def next_start(self, dt):
        return dt + self.offset

    def previous(self, dt):
        return dt - self.offset


class TimeOfDay(OffsetInterval):

    """Time of Day, ie. from 11:00 to 15:00
    """

    def __init__(self, start, end):
        self.offset = pd.offsets.CustomBusinessHour(start=start, end=end, weekmask=[1,1,1,1,1,1,1])

    def __invert__(self):
        return TimeOfDay(start=self.end, end=self.start)

    @property
    def is_overnight(self):
        "Whether the interval goes over night (like from 22:00 --> 03:00)"
        return self.offset.start[0] > self.offset.end[0]

    def next_start(self, dt):
        start_time = self.offset.start[0]

        if dt.time() < start_time:
            # not in period, over night
            #                     dt
            #  -->----------<----------->--------------<-
            #  start   |   end        start     |     end

            # not in period, earlier than start
            #          dt                              
            # --<---------->-----------<-------------->--
            #  end   |   start        end    |      start
            
            # in period, over night, earlier than start
            #            dt
            #  -->----------<----------->--------------<-
            #  start   |   end        start     |     end
            pass
        else:
            # not in period, later than start
            #      dt             
            # --<---------->-----------<-------------->--
            #  end   |   start        end    |      start

            # in period, over night, later than start
            #       dt
            #  -->----------<----------->--------------<-
            #  start   |   end        start     |     end

            # in period
            #                    dt             
            # --<---------->-----------<-------------->--
            #  end   |   start        end    |      start
            dt = dt + pd.offsets.Day()
        return pd.Timestamp.combine(dt, start_time)

    def next_end(self, dt):
        end_time = self.offset.end[0]

        if dt.time() < end_time:
            # in period
            #                    dt             
            # --<---------->-----------<-------------->--
            #  end   |   start        end    |      start
            
            # in period, over night, earlier than end
            #            dt
            #  -->----------<----------->--------------<-
            #  start   |   end        start     |     end

            # not in period, earlier than end
            #          dt                              
            # --<---------->-----------<-------------->--
            #  end   |   start        end    |      start
            pass
        else:
            # not in period, over night
            #                     dt
            #  -->----------<----------->--------------<-
            #  start   |   end        start     |     end

            # not in period, later than end
            #      dt             
            # --<---------->-----------<-------------->--
            #  end   |   start        end    |      start

            # in period, over night, later than end
            #       dt
            #  -->----------<----------->--------------<-
            #  start   |   end        start     |     end
            dt = dt + pd.offsets.Day()

        return pd.Timestamp.combine(dt, end_time)

    def prev_start(self, dt):
        start_time = self.offset.start[0]

        if dt.time() < start_time:
            # not in period, over night
            #                     dt
            #  -->----------<----------->--------------<-
            #  start   |   end        start     |     end

            # not in period, earlier than start
            #          dt                              
            # --<---------->-----------<-------------->--
            #  end   |   start        end    |      start
            
            # in period, over night, earlier than start
            #            dt
            #  -->----------<----------->--------------<-
            #  start   |   end        start     |     end
            dt = dt - pd.offsets.Day()
        else:
            # not in period, later than start
            #      dt             
            # --<---------->-----------<-------------->--
            #  end   |   start        end    |      start

            # in period, over night, later than start
            #       dt
            #  -->----------<----------->--------------<-
            #  start   |   end        start     |     end

            # in period
            #                    dt             
            # --<---------->-----------<-------------->--
            #  end   |   start        end    |      start
            pass
        return pd.Timestamp.combine(dt, start_time)

    def prev_end(self, dt):
        end_time = self.offset.end[0]

        if dt.time() < end_time:
            # in period
            #                    dt             
            # --<---------->-----------<-------------->--
            #  end   |   start        end    |      start
            
            # in period, over night, earlier than end
            #            dt
            #  -->----------<----------->--------------<-
            #  start   |   end        start     |     end

            # not in period, earlier than end
            #          dt                              
            # --<---------->-----------<-------------->--
            #  end   |   start        end    |      start
            dt = dt - pd.offsets.CDay()
        else:
            # not in period, over night
            #                     dt
            #  -->----------<----------->--------------<-
            #  start   |   end        start     |     end

            # not in period, later than end
            #      dt             
            # --<---------->-----------<-------------->--
            #  end   |   start        end    |      start

            # in period, over night, later than end
            #       dt
            #  -->----------<----------->--------------<-
            #  start   |   end        start     |     end
            pass

        return pd.Timestamp.combine(dt, end_time)

    @property
    def start(self):
        return self.offset.start[0]

    @property
    def end(self):
        return self.offset.end[0]

    def __repr__(self):
        return f'TimeOfDay({self.start}, {self.end})'

class DaysOfWeek(OffsetInterval):
    """Day of Week, ie. Monday, Tuesday and Saturday
    """

    def __init__(self, *weekdays, **kwargs):

        self.offset = pd.offsets.CustomBusinessDay(weekmask=self.get_weekmask(weekdays))
        # self.conditions = (DayOfWeek(weekday) for weekday in weekdays)

    def __invert__(self):
        weekmask = [{1:0, 0:1}[d] for d in self.offset.weekmask]
        return DaysOfWeek(weekmask)

    def get_weekmask(self, values):
        "Turn values to week mask (ie. Tuesday & Thursday --> [0, 1, 0, 1, 0, 0, 0])"
        if len(values) == 7 and all(val in (0, 1) for val in values):
            # Already binary
            return values
        
        weekdays_binary = []

        weekday_abbrs = list(calendar.day_abbr)
        weekday_names = list(calendar.day_name)

        if isinstance(values, (list, tuple, set)):
            for i in range(7):
                if weekday_abbrs[i] in values or weekday_names[i] in values:
                    weekdays_binary.append(1)
                else:
                    weekdays_binary.append(0)
        else:
            return values

        return weekdays_binary

    @property
    def weekdays(self):
        mapping = dict(zip(range(7), list(calendar.day_abbr)))
        return [
            mapping[i] 
            for i, val in enumerate(self.offset.weekmask)
            if val
        ]

    def __repr__(self):
        string = ', '.join(self.weekdays)
        return f'<{string}>'

    def rollforward(self, dt):
        dt_rolled = super().rollforward(dt)
        return floor_time(dt_rolled) if dt_rolled != dt else dt_rolled

    def rollback(self, dt):
        dt_rolled = super().rollback(dt)
        return ceil_time(dt_rolled) if dt_rolled != dt else dt_rolled

    def next_end(self, dt):
        # We loop days before we hit a day that 
        # is not on the week mask
        dt = self.rollforward(dt)
        while self.offset.weekmask[(dt + pd.offsets.Day()).weekday()]:
            dt = dt + pd.offsets.Day()
        return ceil_time(dt)

    def prev_start(self, dt):
        # We loop days before we hit a day that 
        # is not on the week mask
        dt = self.rollback(dt)
        while self.offset.weekmask[(dt - pd.offsets.Day()).weekday()]:
            dt = dt - pd.offsets.Day()
        return floor_time(dt)

weekend = DaysOfWeek("Sat", "Sun", access_name="weekend")
weekday = DaysOfWeek("Mon", "Tue", "Wed", "Thu", "Fri", access_name="weekday")

month_end = OffsetInterval(pd.offsets.MonthEnd())
month_begin = OffsetInterval(pd.offsets.MonthBegin())