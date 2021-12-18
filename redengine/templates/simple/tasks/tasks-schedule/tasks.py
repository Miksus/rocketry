
# Put your tasks here

from redengine.tasks import FuncTask
from redengine.extensions import Sequence

# These are some examples of piping tasks

@FuncTask(start_cond="minutely")
def run_minutely():
    print("Runs once a minute")
    ...

@FuncTask(start_cond="hourly")
def run_hourly():
    print("Runs once an hour")
    ...

@FuncTask(start_cond="daily")
def run_daily():
    print("Runs once a day")
    ...

@FuncTask(start_cond="weekly")
def run_weekly():
    print("Runs once a week")
    ...

# Some complex examples
@FuncTask(
    start_cond="""
          daily between 08:00 and 22:00 
          & ~time of day between 12:00 and 14:00
    """
)
def run_daily_complex():
    print("Runs once a day between 08:00 and 22:00 but not at 12:00 to 14:00")
    ...

@FuncTask(start_cond="""weekly on Monday | weekly on Friday""")
def run_weekly_twice():
    print("Runs twice a week: on Monday and on Friday")
    ...