
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