import datetime
from typing import Union
from dateutil.parser import parse

ABBREVIATIONS = {
    'ns': 'nanosecond',
    'μs': 'microsecond',
    'ms': 'millisecond',
    's': 'second',
    'm': 'minute',
    'h': 'hour',

    'nanosecond': 'nanosecond',
    'microsecond': 'microsecond',
    'millisecond': 'millisecond',
    'second': 'second',
    'minute': 'minute',
    'hour': 'hour',
}

def datetime_to_dict(dt):
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

def to_timestamp(dt) -> float:
    if hasattr(dt, "to_pydatetime"):
        dt = dt.to_pydatetime()
    return dt.timestamp()

def to_datetime(s):
    if isinstance(s, datetime.datetime):
        return s
    elif isinstance(s, str):
        return string_to_datetime(s)
    elif hasattr(s, "timestamp"):
        # Is datetime-like. Tests' monkeypatching
        # overrides datetime.datetime thus we cannot
        # always rely on type
        return datetime.datetime.fromtimestamp(s.timestamp())
    else:
        raise TypeError(f"Cannot convert to datetime: {type(s)}")

def to_timedelta(s, **kwargs):
    "Convert object to timedelta"
    if isinstance(s, datetime.timedelta):
        return s
    elif isinstance(s, str):
        return string_to_timedelta(s)
    elif isinstance(s, (int, float)):
        return numb_to_timedelta(s, **kwargs)
    else:
        raise TypeError(f"Cannot convert to timedelta: {type(s)}")

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

def timedelta_to_str(dt, 
                     days_in_year=360, days_in_month=30, 
                     sep=", ", mapping=None, units=None,
                     default_scope="nanoseconds"):

    
    components = timedelta_to_dict(dt, days_in_year=days_in_year, days_in_month=days_in_month, units=units)
    
    # Min and max units (components must be ordered from biggest to smallest units)
    min_unit = default_scope
    for unit, value in components.items():
        if value != 0:
            min_unit = unit
            
    max_unit = default_scope
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

def string_to_datetime(s):
    return parse(s)


def numb_to_timedelta(n: Union[float, int], unit="μs"):
    
    if unit == "ns":
        unit = 'μs'
        n = n / 1000
    units = ABBREVIATIONS[unit] + "s"
    return datetime.timedelta(**{units: n})

def string_to_timedelta(s:str):
    "Convert string to timedelta"

    def is_numeric_char(s):
        return s.isdigit() or s in ('.',)

    def is_wordbreak_char(s):
        return s in (' ', ',', ':', ',')

    def skip_wordbreak(s):
        for pos, char in enumerate(s):
            if not is_wordbreak_char(char):
                break
        return pos

    def get_number(s):
        num = ""
        for pos, char in enumerate(s):
            if is_numeric_char(char):
                num += char
            else:
                break
        return num, pos

    def get_unit(s):
        abbr = ""
        for pos, char in enumerate(s):
            if is_numeric_char(char) or is_wordbreak_char(char):
                break
            else:
                abbr += char
        else:
            # String ended
            pos += 1
        return abbrs[abbr], pos

    def get_hhmmss(s):
        hh, mm, ss = s.split(":")
        return to_microseconds(hour=int(hh), minute=int(mm), second=float(ss))

    # https://github.com/pandas-dev/pandas/blob/e8093ba372f9adfe79439d90fe74b0b5b6dea9d6/pandas/_libs/tslibs/timedeltas.pyx#L296
    abbrs = {
        'millisecond': 'millisecond',
        'ms': 'millisecond',

        'seconds': 'second',
        'second': 'second',
        'sec': 'second',
        's': 'second',

        'minutes': 'minute',
        'minute': 'minute',
        'mins': 'minute',
        'min': 'minute',
        'm': 'minute',

        'hours': 'hour',
        'hour': 'hour',
        'h': 'hour',

        'days': 'day',
        'day': 'day',
        'd': 'day',
    }

    ms = 0
    # Finding out the leading "-"
    is_negative = False
    for i, char in enumerate(s):
        if char == '-':
            is_negative = not is_negative
        elif char == "+":
            continue
        else:
            break
    s = s[i:]
    # Continuing to find the time elements
    while s:
        pos = skip_wordbreak(s)
        s = s[pos:]

        # Example: "-  2.5  days ..."
        # Pos:         ^ 

        numb, pos = get_number(s)
        s = s[pos:]

        if s[0] == ":":
            # Expecting HH:MM:SS
            ms += get_hhmmss(numb + s)
            break

        # Example: "-  2.5  days ..."
        # Pos:            ^ 

        pos = skip_wordbreak(s)
        s = s[pos:]

        # Example: "-  2.5  days ..."
        # Pos:              ^ 

        abbr, pos = get_unit(s)
        s = s[pos:]

        ms += to_microseconds(**{abbr: float(numb)})
    
    if is_negative:
        ms = -ms
    return datetime.timedelta(microseconds=ms)

def to_microseconds(day=0, hour=0, minute=0, second=0, millisecond=0, microsecond=0) -> int:
    "Turn time components to microseconds"
    return microsecond + millisecond * 1_000 + second * int(1e+6) + minute * int(6e+7) + hour * int(3.6e+9) + day * int(8.64e+10)

def to_nanoseconds(day=0, hour=0, minute=0, second=0, millisecond=0, microsecond=0, nanosecond=0) -> int:
    "Turn time components to nanoseconds"
    return nanosecond + microsecond * 1_000 + millisecond * 1_000_000 + second * int(1e+9) + minute * int(6e+10) + hour * int(3.6e+12) + day * int(8.64e+13)