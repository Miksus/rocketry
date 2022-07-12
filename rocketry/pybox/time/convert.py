import datetime
from typing import Union
from dateutil.parser import parse

def to_datetime(s):
    if isinstance(s, datetime.datetime):
        return s
    elif isinstance(s, str):
        return string_to_datetime(s)
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


def string_to_datetime(s):
    return parse(s)


def numb_to_timedelta(n: Union[float, int], unit="ms"):
    multip = {
        "ns": 1/1000,
        "ms": 1,
    }[unit]
    return datetime.timedelta(microseconds=n * multip)

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

    # https://github.com/pandas-dev/pandas/blob/e8093ba372f9adfe79439d90fe74b0b5b6dea9d6/pandas/_libs/tslibs/timedeltas.pyx#L296
    abbrs = {
        'seconds': 'second',
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

    ns = 0
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

        numb, pos = get_number(s)
        s = s[pos:]

        pos = skip_wordbreak(s)
        s = s[pos:]

        abbr, pos = get_unit(s)
        s = s[pos:]

        ns += to_nanoseconds(**{abbr: float(numb)})
    return datetime.timedelta(microseconds=ns / 1000)

def to_nanoseconds(day=0, hour=0, minute=0, second=0, microsecond=0, nanosecond=0) -> int:
    "Turn time components to nanoseconds"
    return nanosecond + microsecond * 1_000 + second * int(1e+9) + minute * int(6e+10) + hour * int(3.6e+12) + day * int(8.64e+13)