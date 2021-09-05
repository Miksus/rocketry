String Parsing
==============

Condition
---------

    >>> from powerbase.parse import parse_condition

Time related
------------

    >>> # Check if the time is between 10 AM and 2 PM
    >>> parse_condition('time of day between 10:00 and 14:00')
    IsPeriod(period=TimeOfDay('10:00', '14:00'))

    >>> # Check if time is after 3 PM (3 PM to 12 PM)
    >>> parse_condition('time of day after 15:00')
    IsPeriod(period=TimeOfDay('15:00', None))

    >>> # Check if time is before 3 PM (3 PM to 12 PM)
    >>> parse_condition('time of day before 15:00')
    IsPeriod(period=TimeOfDay(None, '15:00'))

Task related
------------

The main purpose of these conditions are to provide convenient way
to set a task to run once in a specific interval (ie. day). The syntax is meant to
be as human readable as possible thus it is not as pure in sense of condition logic.

    >>> # Check if the task (not yet declared) has not run between 10 AM and 3 PM. 
    >>> # Useful to set a task to run daily/weekly/monthly.
    >>> parse_condition('daily between 10:00 and 15:00')
    TaskExecutable(task=None, period=TimeOfDay('10:00', '15:00'))

    >>> # Check if the task (not yet declared) has not run after another task named 'other'
    >>> # Useful to set a task run after another has succeeded.
    >>> parse_condition("after 'other' succeeded")
    DependSuccess(task=None, depend_task='other')


See all available string parsers:

    >>> from powerbase.conditions import PARSERS
