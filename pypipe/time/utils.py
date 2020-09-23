
def string_to_datetime(string, formats, ceil=False):
    for fmt in formats:
        try:
            datelike = datetime.datetime.strptime(string, fmt)
        except ValueError:
            continue
        else:
            break
    else:
        raise

    if ceil:
        ceiling = {
            "%S": {"second": 59},
            "%M": {"minute": 59},
            "%H": {"hour": 23}
        }
        for format_key, method in ceiling.items():
            if format_key not in fmt:
                datelike = datelike.replace(**method) if isinstance(method, dict) else method(datelike)
    print(datelike)
    return datelike

import datetime

def ceil_time(dt):
    time_max = datetime.time.max
    replace = {
        elem: getattr(time_max, elem)
        for elem in ("hour", "minute", "second", "microsecond")
    }
    return dt.replace(**replace)

def floor_time(dt):
    time_min = datetime.time.min
    replace = {
        elem: getattr(time_min, elem)
        for elem in ("hour", "minute", "second", "microsecond")
    }
    return dt.replace(**replace)


def ceil_date(dt):
    time_max = datetime.date.max
    replace = {
        elem: getattr(time_max, elem)
        for elem in ("year", "month", "day")
    }
    return dt.replace(**replace)

def floor_date(dt):
    time_min = datetime.date.min
    replace = {
        elem: getattr(time_min, elem)
        for elem in ("year", "month", "day")
    }
    return dt.replace(**replace)

# Conversions
def to_dict(dt):
    return {
        "year": dt.year,
        "month": dt.month,
        "day": dt.day,
        "hour": dt.hour,
        "minute": dt.minute,
        "second": dt.second,
        "microsecond": dt.microsecond,
        "nanosecond": dt.nanosecond if hasattr(dt, "nanosecond") else 0
    }

def to_nanoseconds(day=0, hour=0, minute=0, second=0, microsecond=0, nanosecond=0):
    "Turn time components to nanoseconds"
    return nanosecond + microsecond * 1_000 + second * 1e+9 + minute * 6e+10 + hour * 3.6e+12 + day * 8.64e+13

def to_microsecond(day=0, hour=0, minute=0, second=0, microsecond=0, nanosecond=0):
    "Turn time components to microseconds"
    return to_nanoseconds(day, hour, minute, second, microsecond, nanosecond) / 1_000

def to_second(day=0, hour=0, minute=0, second=0, microsecond=0, nanosecond=0):
    "Turn time components to seconds"
    return to_nanoseconds(day, hour, minute, second, microsecond, nanosecond) / 1e+9

def to_minute(day=0, hour=0, minute=0, second=0, microsecond=0, nanosecond=0):
    "Turn time components to minutes"
    return to_nanoseconds(day, hour, minute, second, microsecond, nanosecond) / 6e+10

def to_hour(day=0, hour=0, minute=0, second=0, microsecond=0, nanosecond=0):
    "Turn time components to hours"
    return to_nanoseconds(day, hour, minute, second, microsecond, nanosecond) / 3.6e+12

def to_day(day=0, hour=0, minute=0, second=0, microsecond=0, nanosecond=0):
    "Turn time components to days"
    return to_nanoseconds(day, hour, minute, second, microsecond, nanosecond) / 8.64e+13