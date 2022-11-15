from rocketry.conds import crontime

@app.task(crontime(minute="*/5"))
def do_simple():
    "Run at every 5th minute"
    ...


@app.task(crontime(minute="*/2", hour="7-18", day_of_month="1,2,3", month="Feb-Aug/2"))
def do_complex():
    """Run at:
        - Every second minute
        - Between 07:00 (7 a.m.) - 18:00 (6 p.m.)
        - On 1st, 2nd and 3rd day of month
        - From February to August every second month
    """
    ...
