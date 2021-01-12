
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


def timedelta_to_dict(dt, days_in_year=365, days_in_month=30, units=None):
    
    total_seconds = dt.total_seconds()
    nanoseconds = total_seconds * 1e+9

    components = {}
    if units == "all":
        allowed_units = (
            "years", "months", "weeks", 
            "days", "hours", "minutes", 
            "seconds", "microseconds", 
            "nanoseconds")
    elif units == "fixed" or units is None:
        # Only fixed length units
        allowed_units = (
            "days", "hours", "minutes", 
            "seconds", "microseconds", 
            "nanoseconds")
    else:
        allowed_units = units

    # Non fixed units
    if "years" in allowed_units:
        components["years"] = int(nanoseconds // (8.64e+13 * days_in_year))
        nanoseconds = nanoseconds - (components["years"] * 8.64e+13 * days_in_year)
    
    if "months" in allowed_units:
        components["months"] = int(nanoseconds // (8.64e+13 * days_in_month))
        nanoseconds = nanoseconds - (components["months"] * 8.64e+13 * days_in_month)
    
    # Alternating units
    if "weeks" in allowed_units:
        components["weeks"] = int(nanoseconds // (8.64e+13 * 7))
        nanoseconds = nanoseconds - components["weeks"] * 8.64e+13 * 7
    
    # Fixed units
    if "days" in allowed_units:
        components["days"] = int(nanoseconds // 8.64e+13)
        nanoseconds = nanoseconds - components["days"] * 8.64e+13
    
    if "hours" in allowed_units:
        components["hours"] = int(nanoseconds // 3.6e+12)
        nanoseconds = nanoseconds - components["hours"] * 3.6e+12
    
    if "minutes" in allowed_units:
        components["minutes"] = int(nanoseconds // 6e+10)
        nanoseconds = nanoseconds - components["minutes"] * 6e+10
    
    if "seconds" in allowed_units:
        components["seconds"] = int(nanoseconds // 1e+9)
        nanoseconds = nanoseconds - components["seconds"] * 1e+9
    
    if "microseconds" in allowed_units:
        components["microseconds"] = int(nanoseconds // 1_000)
        nanoseconds = nanoseconds - components["microseconds"] * 1_000
    
    # And the rest is nanoseconds
    if "nanoseconds" in allowed_units:
        components["nanoseconds"] = int(nanoseconds)

    return components

def timedelta_to_str(dt, days_in_year=360, days_in_month=30, sep=", ", mapping=None, units=None):

    
    components = timedelta_to_dict(dt, days_in_year=days_in_year, days_in_month=days_in_month, units=units)
    
    # Min and max units (components must be ordered from biggest to smallest units)
    for unit, value in components.items():
        if value != 0:
            min_unit = unit
            
    for unit, value in components.items():
        if value != 0:
            # Max currently found non zero
            max_unit = unit
            break
            
    
    # Determine mapping
    if mapping is None:
        mapping = {
            "years": " years",
            "months": " months",
            "weeks": " weeks",
            "days": " days",
            "hours": " hours",
            "minutes": " minutes",
            "seconds": " seconds",
            "microseconds": " microseconds",
            "nanoseconds": " nanoseconds",
        }
    elif mapping == "semishort":
        mapping = {
            "years": " years",
            "months": " months",
            "weeks": " weeks",
            "days": " days",
            "hours": " h",
            "minutes": " min",
            "seconds": " sec",
            "microseconds": " microsec",
            "nanoseconds": "nanosec",
        }
    elif mapping == "short":
        mapping = {
            "years": "Y",
            "months": "M",
            "weeks": "W",
            "days": "d",
            "hours": "h",
            "minutes": "m",
            "seconds": "s",
            "microseconds": "ms",
            "nanoseconds": "ns",
        }

    # String format
    s = ""
    is_min_reached = False
    is_max_reached = False
    for unit, value in components.items():
        is_min_reached = min_unit == unit
        is_max_reached = is_max_reached or unit == max_unit

        unit_name = mapping[unit]
        if max_unit == unit:
            s = s + f"{value}{unit_name}"
        elif is_max_reached:
            s = s + f"{sep}{value}{unit_name}"
            
        if is_min_reached:
            break
    return s