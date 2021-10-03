from redengine.tasks import FuncTask

@FuncTask(start_cond="minutely")
def example_task():
    "This runs once a minute"
    ...

@FuncTask(start_cond="hourly")
def example_task():
    "This runs once an hour"
    ...

@FuncTask(start_cond="daily")
def example_task():
    "This runs once a day"
    ...

@FuncTask(start_cond="weekly")
def example_task():
    "This runs once a week"
    ...

@FuncTask(start_cond="monthly")
def example_task():
    "This runs once a month"
    ...

@FuncTask(start_cond="every 3 days")
def example_task():
    "This runs once in 3 days"
    ...

@FuncTask(start_cond="every 1 hour, 30 min")
def example_task():
    "This runs once in 1 hour and 30 minutes"
    ...

# Time with options
@FuncTask(start_cond="daily between 08:00 and 11:00")
def example_task():
    "This runs once a day between 8 AM and 11 AM"
    ...

@FuncTask(start_cond="weekly between Monday and Friday")
def example_task():
    """This runs once a week between Monday and Friday 
    (including both of these days)"""
    ...


# More complex
# ------------

@FuncTask(start_cond="""
    daily between 08:00 and 11:00 
    | daily between 13:00 and 16:00
""")
def example_task():
    """This runs once in the morning and once in the afternoon.
    See we use '|' operator which is 'OR' operator"""
    ...

@FuncTask(start_cond="""
    weekly on Monday
    | weekly on Tuesday
""")
def example_task():
    """This runs once on Monday and once on Tuesday.
    See we use '|' operator which is 'OR' operator"""
    ...

@FuncTask(start_cond="""
    (weekly on Monday & time of day between 08:00 and 11:00)
    | (weekly on Tuesday & time of day between 19:00 and 23:00)
""")
def example_task():
    """This runs once on Monday mornign and once on Tuesday evening.
    See we use '|' operator which is 'OR' operator"""
    ...