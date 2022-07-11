@app.task("minutely before 45")
def do_minutely():
    ...

@app.task("hourly after 45:00")
def do_hourly():
    ...

@app.task("daily between 08:00 and 14:00")
def do_daily():
    ...

@app.task("weekly on Monday")
def do_weekly():
    ...

@app.task("monthly starting 3rd")
def do_monthly():
    ...