
import datetime
import pytest
from rocketry.time.interval import (
    TimeOfMinute,
    TimeOfDay,
    TimeOfHour,
    TimeOfMonth,
    TimeOfSecond,
    TimeOfWeek,
    TimeOfYear
)

MS_IN_MILLISECOND = 1000
MS_IN_SECOND = int(1e+6)
MS_IN_MINUTE = int(1e+6 * 60)
MS_IN_HOUR   = int(1e+6 * 60 * 60)
MS_IN_DAY    = int(1e+6 * 60 * 60 * 24)

def pytest_generate_tests(metafunc):
    if metafunc.cls is not None:

        method_name = metafunc.function.__name__
        cls = metafunc.cls
        params = []
        if method_name == "test_closed":
            params = cls.scen_closed
        elif method_name == "test_open":
            return
        elif method_name == "test_open_left":
            params = cls.scen_open_left
        elif method_name == "test_open_right":
            params = cls.scen_open_right
        elif method_name == "test_time_point":
            params = cls.scen_time_point
        elif method_name == "test_starting":
            params = cls.scen_starting
        elif method_name == "test_value_error":
            params = cls.scen_value_error
        else:
            return

        argnames = [arg for arg in metafunc.fixturenames if arg in ('start', 'end', "expected_start", "expected_end", "time_point")]

        idlist = []
        argvalues = []
        argvalues = []
        for scen in params:
            idlist.append(scen.pop("id", f'{repr(scen.get("start"))}, {repr(scen.get("end"))}'))
            argvalues.append(tuple(scen[name] for name in argnames))
        metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")

class ConstructTester:

    def test_closed(self, start, end, expected_start, expected_end):
        time = self.cls(start, end)
        assert not time.is_full()
        assert expected_start == time._start
        assert expected_end == time._end

    def test_open(self):
        time = self.cls(None, None)
        assert time.is_full()
        assert 0 == time._start
        assert self.max_ms == time._end

    def test_open_left(self, end, expected_end, **kwargs):
        time = self.cls(None, end)
        assert not time.is_full()
        assert 0 == time._start
        assert expected_end == time._end

    def test_open_right(self, start, expected_start, **kwargs):
        time = self.cls(start, None)
        assert not time.is_full()
        assert expected_start == time._start
        assert self.max_ms == time._end

    def test_time_point(self, start, expected_start, expected_end, **kwargs):
        time = self.cls(start, time_point=True)
        assert not time.is_full()
        assert expected_start == time._start
        assert expected_end == time._end

        time = self.cls.at(start)
        assert not time.is_full()
        assert expected_start == time._start
        assert expected_end == time._end

    def test_starting(self, start, expected_start, **kwargs):
        time = self.cls(start, starting=True)
        assert time.is_full()
        assert expected_start == time._start
        assert expected_start == time._end

        time = self.cls.starting(start)
        assert time.is_full()
        assert expected_start == time._start
        assert expected_start == time._end

    def test_value_error(self, start, end):
        with pytest.raises(ValueError):
            time = self.cls(start, end)

class TestTimeOfSecond(ConstructTester):

    cls = TimeOfSecond

    max_ms = MS_IN_SECOND

    scen_closed = [
        {
            "start": "15.005",
            "end": "45.005",
            "expected_start": 15 * MS_IN_MILLISECOND + 5,
            "expected_end": 45 * MS_IN_MILLISECOND + 5,
        },
       {
            "start": 15,
            "end": 45,
            "expected_start": 15 * MS_IN_MILLISECOND,
            "expected_end": 46 * MS_IN_MILLISECOND,
        },
       {
            "start": 15.005,
            "end": 45.005,
            "expected_start": 15 * MS_IN_MILLISECOND + 5,
            "expected_end": 45 * MS_IN_MILLISECOND + 5,
        },
    ]

    scen_open_left = [
        {
            "end": 45,
            "expected_end": 46 * MS_IN_MILLISECOND
        }
    ]
    scen_open_right = [
        {
            "start": 45,
            "expected_start": 45 * MS_IN_MILLISECOND
        }
    ]
    scen_time_point = [
        {
            "start": 500,
            "expected_start": 500 * MS_IN_MILLISECOND,
            "expected_end": 501 * MS_IN_MILLISECOND,
        }
    ]
    scen_starting = [
        {
            "start": 500,
            "expected_start": 500 * MS_IN_MILLISECOND,
        }
    ]
    scen_value_error = [
        {
            "start": 1001,
            "end": None
        },
        {
            "start": 1000.001,
            "end": None
        },
        {
            "start": "1001",
            "end": None
        },
        {
            "start": "asd",
            "end": None
        },
    ]

class TestTimeOfMinute(ConstructTester):

    cls = TimeOfMinute

    max_ms = MS_IN_MINUTE

    scen_closed = [
        {
            "start": "15",
            "end": "45",
            "expected_start": 15 * MS_IN_SECOND,
            "expected_end": 45 * MS_IN_SECOND,
        },
        {
            "start": "15.000",
            "end": "45.000",
            "expected_start": 15 * MS_IN_SECOND,
            "expected_end": 45 * MS_IN_SECOND,
        },
        {
            "start": "15.5",
            "end": "45.5",
            "expected_start": 15 * MS_IN_SECOND + MS_IN_MILLISECOND * 500,
            "expected_end": 45 * MS_IN_SECOND + MS_IN_MILLISECOND * 500,
        },
        {
            "start": "15.005",
            "end": "45.005",
            "expected_start": 15 * MS_IN_SECOND + MS_IN_MILLISECOND * 5,
            "expected_end": 45 * MS_IN_SECOND + MS_IN_MILLISECOND * 5,
        },
        {
            "start": "15.000005",
            "end": "45.000005",
            "expected_start": 15 * MS_IN_SECOND + 5,
            "expected_end": 45 * MS_IN_SECOND + 5,
        },
        {
            "start": 15,
            "end": 45,
            "expected_start": 15 * MS_IN_SECOND,
            "expected_end": 46 * MS_IN_SECOND,
        },
        {
            "start": 15.005,
            "end": 45.005,
            "expected_start": 15 * MS_IN_SECOND + 5 * MS_IN_MILLISECOND,
            "expected_end": 45 * MS_IN_SECOND + 5 * MS_IN_MILLISECOND,
        },
    ]

    scen_open_left = [
        {
            "end": "45.00",
            "expected_end": 45 * MS_IN_SECOND
        }
    ]
    scen_open_right = [
        {
            "start": "45",
            "expected_start": 45 * MS_IN_SECOND
        }
    ]
    scen_time_point = [
        {
            "start": "12:00",
            "expected_start": 12 * MS_IN_SECOND,
            "expected_end": 13 * MS_IN_SECOND,
        }
    ]
    scen_starting = [
        {
            "start": "12:00",
            "expected_start": 12 * MS_IN_SECOND,
        }
    ]
    scen_value_error = [
        {
            "start": 60,
            "end": None
        }
    ]

class TestTimeOfHour(ConstructTester):

    cls = TimeOfHour

    max_ms = MS_IN_HOUR

    scen_closed = [
        {
            "start": "15:00",
            "end": "45:00",
            "expected_start": 15 * MS_IN_MINUTE,
            "expected_end": 45 * MS_IN_MINUTE,
        },
        {
            "start": 15,
            "end": 45,
            "expected_start": 15 * MS_IN_MINUTE,
            "expected_end": 46 * MS_IN_MINUTE,
        },
        {
            "start": "15:05.5",
            "end": "45:10.005",
            "expected_start": 15 * MS_IN_MINUTE + 5 * MS_IN_SECOND + MS_IN_MILLISECOND * 500,
            "expected_end": 45 * MS_IN_MINUTE + 10 * MS_IN_SECOND + MS_IN_MILLISECOND * 5,
        },
    ]

    scen_open_left = [
        {
            "end": "45:00",
            "expected_end": 45 * MS_IN_MINUTE
        }
    ]
    scen_open_right = [
        {
            "start": "45:00",
            "expected_start": 45 * MS_IN_MINUTE
        }
    ]
    scen_time_point = [
        {
            "start": "12:00",
            "expected_start": 12 * MS_IN_MINUTE,
            "expected_end": 13 * MS_IN_MINUTE,
        }
    ]
    scen_starting = [
        {
            "start": "12:00",
            "expected_start": 12 * MS_IN_MINUTE,
        }
    ]

    scen_value_error = [
        {
            "start": 60,
            "end": None
        },
        {
            "start": None,
            "end": "60:01"
        },
        {
            # Float makes not much sense
            "start": 2.5,
            "end": None
        },
        {
            "start": "invalid",
            "end": None
        },
    ]

class TestTimeOfDay(ConstructTester):

    cls = TimeOfDay

    max_ms = 24 * MS_IN_HOUR

    scen_closed = [
        {
            "start": "10:00",
            "end": "12:00",
            "expected_start": 10 * MS_IN_HOUR,
            "expected_end": 12 * MS_IN_HOUR,
        },
        {
            "start": 10,
            "end": 12,
            "expected_start": 10 * MS_IN_HOUR,
            "expected_end": 13 * MS_IN_HOUR,
        },
        {
            "start": {"hour": 10, "second": 20},
            "end": {"hour": 13, "second": 20},
            "expected_start": 10 * MS_IN_HOUR + 20 * MS_IN_SECOND,
            "expected_end": 13 * MS_IN_HOUR + 20 * MS_IN_SECOND,
        },
    ]

    scen_open_left = [
        {
            "end": "12:00",
            "expected_end": 12 * MS_IN_HOUR
        }
    ]
    scen_open_right = [
        {
            "start": "12:00",
            "expected_start": 12 * MS_IN_HOUR
        }
    ]
    scen_time_point = [
        {
            "start": "12:00",
            "expected_start": 12 * MS_IN_HOUR,
            "expected_end": 13 * MS_IN_HOUR,
        },
        {
            "start": "23:00",
            "expected_start": 23 * MS_IN_HOUR,
            "expected_end": 0,
        },
        {
            "start": "23:01",
            "expected_start": 23 * MS_IN_HOUR + MS_IN_MINUTE,
            "expected_end": MS_IN_MINUTE,
        },
    ]
    scen_starting = [
        {
            "start": "12:00",
            "expected_start": 12 * MS_IN_HOUR,
        }
    ]
    scen_value_error = [
        {
            "start": -1,
            "end": None,
        },
        {
            "start": "asd",
            "end": None,
        },
        {
            "start": 24,
            "end": None,
        },
        {
            "start": None,
            "end": "24:01",
        },
        {
            # Float makes not much sense
            "start": 2.5,
            "end": None
        },
    ]


class TestTimeOfWeek(ConstructTester):

    cls = TimeOfWeek

    max_ms = 7 * MS_IN_DAY

    scen_closed = [
        {
            # Spans from Tue 00:00:00 to Wed 23:59:59 999
            "start": "Tue",
            "end": "Wed",
            "expected_start": 1 * MS_IN_DAY,
            "expected_end": 3 * MS_IN_DAY,
        },
        {
            # Spans from Tue 00:00:00 to Wed 23:59:59 999
            "start": "Tuesday",
            "end": "Wednesday",
            "expected_start": 1 * MS_IN_DAY,
            "expected_end": 3 * MS_IN_DAY,
        },
        {
            # Spans from Tue 00:00:00 to Wed 23:59:59 999
            "start": 2,
            "end": 3,
            "expected_start": 1 * MS_IN_DAY,
            "expected_end": 3 * MS_IN_DAY,
        },
    ]

    scen_open_left = [
        {
            "end": "Tue",
            "expected_end": 2 * MS_IN_DAY # Tuesday 23:59:59 ...
        }
    ]
    scen_open_right = [
        {
            "start": "Tue",
            "expected_start": 1 * MS_IN_DAY # Tuesday 00:00:00
        }
    ]
    scen_time_point = [
        {
            "start": "Tue",
            "expected_start": 1 * MS_IN_DAY,
            "expected_end": 2 * MS_IN_DAY,
        }
    ]
    scen_starting = [
        {
            "start": "Tue",
            "expected_start": 1 * MS_IN_DAY,
        }
    ]
    scen_value_error = [
        {
            "start": 0,
            "end": None
        },
        {
            "start": "Asd",
            "end": None
        },
        {
            # Float makes not much sense
            "start": 2.5,
            "end": None
        },
    ]


class TestTimeOfMonth(ConstructTester):

    cls = TimeOfMonth

    max_ms = 31 * MS_IN_DAY

    scen_closed = [
        {
            "start": "2.",
            "end": "3.",
            "expected_start": 1 * MS_IN_DAY,
            "expected_end": 3 * MS_IN_DAY,
        },
        {
            "start": "2nd",
            "end": "4th",
            "expected_start": 1 * MS_IN_DAY,
            "expected_end": 4 * MS_IN_DAY,
        },
        {
            "start": 2,
            "end": 4,
            "expected_start": 1 * MS_IN_DAY,
            "expected_end": 4 * MS_IN_DAY,
        },
    ]

    scen_open_left = [
        {
            "end": "3.",
            "expected_end": 3 * MS_IN_DAY
        }
    ]
    scen_open_right = [
        {
            "start": "2.",
            "expected_start": 1 * MS_IN_DAY
        }
    ]
    scen_time_point = [
        {
            "start": "2.",
            "expected_start": 1 * MS_IN_DAY,
            "expected_end": 2 * MS_IN_DAY,
        }
    ]
    scen_starting = [
        {
            "start": "2.",
            "expected_start": 1 * MS_IN_DAY,
        }
    ]
    scen_value_error = [
        {
            "start": 0,
            "end": None,
        },
        {
            "start": None,
            "end": 32,
        },
        {
            "start": "33.",
            "end": None
        },
        {
            # Float makes not much sense
            "start": 2.5,
            "end": None
        },
    ]

class TestTimeOfYear(ConstructTester):

    cls = TimeOfYear

    max_ms = 366 * MS_IN_DAY # Leap year has 366 days

    scen_closed = [
        {
            "start": "February",
            "end": "April",
            "expected_start": 31 * MS_IN_DAY,
            "expected_end": (31 + 29 + 31 + 30) * MS_IN_DAY - 1,
        },
        {
            "start": "Feb",
            "end": "Apr",
            "expected_start": 31 * MS_IN_DAY,
            "expected_end": (31 + 29 + 31 + 30) * MS_IN_DAY - 1,
        },
        {
            "start": 2,
            "end": 4,
            "expected_start": 31 * MS_IN_DAY,
            "expected_end": (31 + 29 + 31 + 30) * MS_IN_DAY - 1,
        },
    ]

    scen_open_left = [
        {
            "end": "Apr",
            "expected_end": (31 + 29 + 31 + 30) * MS_IN_DAY - 1
        },
        {
            "end": "Jan",
            "expected_end": 31 * MS_IN_DAY - 1
        },
    ]
    scen_open_right = [
        {
            "start": "Apr",
            "expected_start": (31 + 29 + 31) * MS_IN_DAY
        },
        {
            "start": "Dec",
            "expected_start": (366 - 31) * MS_IN_DAY
        },
    ]
    scen_time_point = [
        {
            "start": "Jan",
            "expected_start": 0,
            "expected_end": 31 * MS_IN_DAY - 1,
        },
        {
            "start": "Feb",
            "expected_start": 31 * MS_IN_DAY,
            "expected_end": (31 + 29) * MS_IN_DAY - 1,
        },
        {
            "start": "Dec",
            "expected_start": (366 - 31) * MS_IN_DAY,
            "expected_end": 366 * MS_IN_DAY - 1,
        },
    ]
    scen_starting = [
        {
            "start": "Feb",
            "expected_start": 31 * MS_IN_DAY,
        }
    ]
    scen_value_error = [
        {
            "start": 0,
            "end": None,
        },
        {
            "start": None,
            "end": 13,
        },
        {
            # Float makes not much sense
            "start": 2.5,
            "end": None
        },
    ]

@pytest.mark.parametrize("cls", [TimeOfSecond, TimeOfMinute, TimeOfHour, TimeOfDay])
def test_type_error(cls):
    with pytest.raises(TypeError):
        time = cls.starting(lambda: None)
    with pytest.raises(TypeError):
        time = cls.starting(datetime.datetime(2022, 1, 1))
    with pytest.raises(TypeError):
        time = cls.starting(datetime.timedelta(days=2))

    with pytest.raises(ValueError):
        time = cls(time_point=True)
