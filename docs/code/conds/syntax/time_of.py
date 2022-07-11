@app.task("time of minute before 45")
def do_constantly_minute_before():
    ...

@app.task("time of hour after 45:00")
def do_constantly_hour_after():
    ...

@app.task("time of day between 08:00 and 14:00")
def do_constantly_day_between():
    ...

@app.task("time of week on Monday")
def do_constantly_week_on():
    ...
