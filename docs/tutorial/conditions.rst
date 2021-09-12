Writing conditions
==================

Conditions are vital part of Red Engine system
as they are responsible of determining when a 
task may start. They also can be used to determine
when the session will end or when a task will be killed.

Under the hood, there are condition objects 
which states are inspected from the magic method 
``__bool__`` and which can be combined using logical
operations. On top of this, there has been built 
more intuitive syntax to compose these objects.

This syntax is used, for example, in the ``start_cond``
section of a task in ``tasks.yaml`` files consumed by 
the YAMLTaskLoader. 


Run the task on specific times
------------------------------

- Run once a day
    - ``daily``
- Run once a day between 1 PM and 5 PM
    - ``daily between 13:00 and 05:00``
- Run once a week
    - ``weekly``
- Run once a week on Monday
    - ``weekly on Monday``
- Run once a week between Monday and Friday
    - ``weekly between Monday and Friday``
- Run once a month
    - ``monthly``
- Run every 1 hour
    - ``every 1 hour``
- Run every 3 days, 1 hour, 30 minutes (or anything that ``pandas.TimeDelta`` allows)
    - ``every 3 days 1 hour 30 min``

There is also the conditions ``time of ...`` which 
inspect only whether the current time is in the 
given interval and is not linked to any tasks.
Therefore, such condition alone would cause the 
task to be started constantly when the interval
is fulfilled. These are useful for more complex
examples which we will cover later.

- Run all the time when time is between 5 AM and 10 AM.
    - ``time of day between 05:00 and 10:00``
- Run all the time when it's Monday, Tuesday or Wednesday.
    - ``time of week between Monday and Wednesday``


Run the task after another
--------------------------

One can pipe tasks using also
:class:`redengine.ext.Sequence` but there is also
a condition to make task pipelines. Which is to be 
preferred depends on the complexity of the pipelines.
Simple relations can be done with a condition but 
clusters of pipelines are possibly more maintainabe
as sequences.

- Run once after task `other` succeeded
    - ``after task 'other' succeeded``
- Run once after task `other` failed
    - ``after task 'other' failed``
- Run once after task `other` failed or succeeded
    - ``after task 'other' finished``


Complex conditions
------------------

The conditions also can be constructed using logical 
expressions such as ``and``, ``or`` and ``not`` and 
they can be nested using parentheses. Therefore it 
is possible to create complex condition logic fairly
easily. 

These logical operations are formed using the symbols
``&``, ``|`` and ``~`` which corresponds to ``AND``, 
``OR`` and ``NOT`` respectively.

Some examples:

- Run twice a day: once between 8 AM and 10 AM, and once between 5 PM and 6 PM
    - ``daily between 08:00 and 10:00 | daily between 17:00 and 18:00``
- Run daily between 8 AM and 10 AM from Monday to Friday
    - ``daily between 08:00 and 10:00 & time of week between Monday and Friday``
- Run once when either: 'scraper-1' and 'transformer-1' succeeded or 'scraper-2' and 'transformer-2' succeeded
    - | ``(after task 'scraper-1' succeeded & after task 'transformer-1' succeeded)``
      | ``| (after task 'scraper-2' succeeded & after task 'transformer-2' succeeded)``