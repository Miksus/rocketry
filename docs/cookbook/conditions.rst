Condition Cookbook
==================

This section provide examples of various condition
patterns to give further ideas. How conditions work
is not discussed in this section.

Time Related
------------

Run at specific time
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from rocketry.conds import minutely, hourly, daily, weekly, monthly

    @app.task(minutely.at("45"))
    def do_minutely():
        ... # Runs once a minute, 45 seconds past full minute

    @app.task(hourly.at("30:00"))
    def do_hourly():
        ... # Runs half past

    @app.task(daily.at("08:00"))
    def do_daily():
        ... # Runs at 8 a.m.

    @app.task(weekly.at("Mon"))
    def do_weekly():
        ... # Runs on Monday

    @app.task(monthly.at("5th"))
    def do_weekly():
        ... # Runs on 5th day of month

Run using Cron
^^^^^^^^^^^^^^

There is also a cron condition that works
the same as the official cron specifications.
You might find `crontab.guru <https://crontab.guru/>`_
useful to come up with the correct statement.

.. code-block:: python

    from rocketry.conds import cron

    @app.task(cron("* 2 * * *"))
    def do_things():
        ...

Run twice a week at different times
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This example runs in two instances:

- Runs on Monday morning
- Runs on Friday evening

.. code-block:: python

    from rocketry.conds import daily, time_of_week, time_of_day

    @app.task(
        daily 
        & (
            (time_of_week.at("Mon") & time_of_day.between("06:00", "12:00"))
            | (time_of_week.at("Fri") & time_of_day.between("18:00", "23:00"))
        )
    )
    def do_things():
        ...

.. note::

    The task runs at maximum of once a day thus we need to use only once the 
    condition ``daily``. The other conditions simply restrict the time span.

Run daily on work days
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from datetime import date
    from rocketry.conds import daily

    HOLIDAYS = [
        date(2023, 1, 1), # New Year's Day
        date(2023, 1, 6), # Epiphany
        date(2023, 4, 7), # Good Friday
        ...
    ]

    @app.cond()
    def is_work_day():
        today = date.today()
        on_weekend = today.weekday in (5, 6)
        on_holiday = today in HOLIDAYS
        return not on_weekend and not on_holiday

    @app.task(daily & is_work_day)
    def do_things():
        ...

.. note::

    Tip: you can use Pandas calendars to generate the holiday list.

IO Related
----------

File Exists
^^^^^^^^^^^


.. code-block:: python

    from rocketry.conds import daily

    @app.cond()
    def file_exists(file):
        return Path(file).is_file()

    @app.task(daily & file_exists("myfile.csv"))
    def do_things():
        ...