from rocketry.conds import daily, hourly, minutely, monthly, weekly


@app.task(minutely)
def do_minutely():
    ...

@app.task(hourly)
def do_hourly():
    ...

@app.task(daily)
def do_daily():
    ...

@app.task(weekly)
def do_weekly():
    ...

@app.task(monthly)
def do_monthly():
    ...
