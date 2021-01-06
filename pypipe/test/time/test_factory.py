# TODO

#from pypipe.builtin.time import TimeInterval, TimeDelta, TimeCycle, TimePeriod
#
#from pypipe.builtin.time import TimeOfDay, DaysOfWeek#, period_factory
#
#import datetime

def test_factory_between_timeofday():
    # Actual test
    time = period_factory.between("10:00", "11:00")

    assert isinstance(time, TimeOfDay)

def test_factory_between_daysofweek():
    # Actual test
    time = period_factory.between("Mon", "Fri")

    assert isinstance(time, DaysOfWeek)

def test_factory_past():
    # Actual test
    time = period_factory.past("1 days")

    assert isinstance(time, TimeDelta)

def test_factory_from():
    # Actual test
    time = period_factory.from_("Mon")

    assert isinstance(time, TimeCycle)


def test_when_cycle():
    for string in (
        #"monthly",
        #"monthly starting 5"
        #"monthly starting 5th"
        #"monthly starting 5th"
        "weekly",
        "weekly starting friday",
        "weekly ending friday",
        "daily",
        "daily starting 10:00",
        "daily ending 10:00",
        "hourly",
        "hourly starting 15",
        "hourly ending 15",
        "minutely"
    ):
        time = period_factory.when(string)

        assert isinstance(time, TimeCycle)

def test_when_interval():
    for string in (
        #"monthly starting 5",
        "weekly between tuesday and friday",
        "daily between 10:00 and 15:00",
        "hourly between 30 and 45",
        "minutely between 15 and 30"
    ):
        print(string)
        time = period_factory.when(string)

        assert isinstance(time, TimeInterval)

    for string in (
        #"monthly starting 5",
        "weekly before friday",
        "weekly after friday",
        "daily before 12:00",
        "daily after 12:00",
        "hourly before 15",
        "hourly after 15",
        "minutely before 15",
        "minutely after 15",
    ):
        time = period_factory.when(string)

        assert isinstance(time, TimeInterval)