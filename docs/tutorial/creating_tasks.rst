
.. _creating-tasks:
 
Creating Tasks
==============

This section is a simple showcase of how tasks can look like. 


Practical Examples
------------------

Simple notification for late bird users:

.. code-block:: python

    from redengine.tasks import FuncTask
    from win32api import MessageBox

    @FuncTask(start_cond="hourly & time of day 23:00 and 06:00 & time of week between Mon and Fri")
    def notify_sleep():
        """Task that urges the user to shut down 
        the computer and go to sleep. On weekend
        the user can stay up late."""
        MessageBox(0, "Alert", "Please go to sleep.")
        
Simple pipeline with parameter:

.. code-block:: python

    import pandas as pd
    from pandas.tseries.offsets import Day
    from sqlalmchemy import create_engine

    @FuncArg.to_session()
    def report_date():
        "Parameter for report date"
        return pd.Timestamp("now") - Day(1)

    @FuncTask(start_cond="daily after 08:00", name="data-import")
    def import_data(report_date):
        "Load daily batch in"
        engine = create_engine(...)
        file = Path("C:/Temp") / f"{report_date:%Y-%m-%d}_mybatch.csv"

        # Extract and import
        df = pd.read_csv(file)
        df.to_sql('mytable', if_exists="append", con=engine)

    @FuncTask(start_cond="after task 'data-import' succeeded", name="data-process")
    def process_data(report_date):
        "Transform the data"
        engine = create_engine(...)

        # Extract
        df = pd.read_sql(
            'SELECT * FROM mytable WHERE rep_date = :report_date', 
            params={"report_date": report_date},
            con=engine
        )

        # Do some transformation
        df = df.groupby(["id", "subid", "report_date"])["values"].sum()

        # import
        df.to_sql("mytable_cleaned", if_exists="append", con=engine)

    @FuncTask(start_cond="after task 'data-process'", name="data-report")
    def report_data(report_date):
        "Report the data"
        engine = create_engine(...)

        # Extract
        df = pd.read_sql(
            'SELECT * FROM mytable_cleaned WHERE report_date = :report_date', 
            params={"report_date": report_date},
            con=engine
        )
        # Send the data whatever way
        send_data(df)