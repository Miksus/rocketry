Condition Parsing
=================

Conditions for when a task can start, when a task 
should stop or when the system should be shut down
can be formed from intuitive strings. This section
lists different ways to compose such strings for 
different needs.

See :ref:`creating-task` for how to utilize
these strings in starting or ending conditions 
of tasks.


Condition
---------

    >>> from redengine.parse import parse_condition

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

Inspect if a task has started/failed/succeeded/terminated/inacted:

    >>> parse_condition("task 'other' has started")
    TaskStarted(task='other')

    >>> parse_condition("task 'other' has succeeded")
    TaskSucceeded(task='other')

    >>> parse_condition("task 'other' has failed")
    TaskFailed(task='other')

    >>> parse_condition("task 'other' has finished")
    TaskFinished(task='other')

    >>> parse_condition("task 'other' has terminated")
    TaskTerminated(task='other')

    >>> parse_condition("task 'other' has inacted")
    TaskInacted(task='other')


All of these also accepts passing the timespan:

    >>> parse_condition("task 'other' has succeeded this hour")
    TaskSucceeded(task='other', period=TimeOfHour(None, None))

    >>> parse_condition("task 'other' has succeeded today")
    TaskSucceeded(task='other', period=TimeOfDay(None, None))

    >>> parse_condition("task 'other' has succeeded this week")
    TaskSucceeded(task='other', period=TimeOfWeek(None, None))

    >>> parse_condition("task 'other' has succeeded this month")
    TaskSucceeded(task='other', period=TimeOfMonth(None, None))

Or specify the before/between/after:

    >>> parse_condition("task 'other' has succeeded today after 10:00")
    TaskSucceeded(task='other', period=TimeOfDay('10:00', None))

    >>> parse_condition("task 'other' has succeeded today before 14:00")
    TaskSucceeded(task='other', period=TimeOfDay(None, '14:00'))

    >>> parse_condition("task 'other' has succeeded today between 10:00 and 14:00")
    TaskSucceeded(task='other', period=TimeOfDay('10:00', '14:00'))


There are also conditions meant for building common starting condition mechanism out of the box
like "run a task once a day" or "run a task after another task succeeded".
These conditions are not as pure as others in terms of syntax but they aim for convenience. 
One should not use these conditions elsewhere than setting starting conditions for tasks.
Note that the ``task`` argument is supplied automatically to the conditions when the condition 
is assigned to a task.

    >>> # Check if the task (not yet declared) has not run between 10 AM and 3 PM. 
    >>> # Useful to set a task to run daily/weekly/monthly.
    >>> parse_condition('daily between 10:00 and 15:00')
    TaskExecutable(task=None, period=TimeOfDay('10:00', '15:00'))

    >>> # Check if the task (not yet declared) has not run after another task named 'other'
    >>> # Useful to set a task to run after another has succeeded.
    >>> parse_condition("after task 'other' succeeded")
    DependSuccess(task=None, depend_task='other')


See all available string parsers:

    >>> from redengine.conditions import PARSERS
