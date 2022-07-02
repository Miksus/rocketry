@app.task("every 10 seconds")
def do_continuously():
    ...

@app.task("daily after 07:00")
def do_daily_after_seven():
    ...

@app.task("hourly & time of day between 22:00 and 06:00")
def do_hourly_at_night():
    ...

@app.task("weekly on Monday | weekly on Saturday")
def do_twice_a_week():
    ...

@app.task("""hourly & (
    time of day between 09:00 and 12:00 
    | time of week between Sat and Sun
)""")
def do_complex():
    ...