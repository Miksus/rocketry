from rocketry.conds import minutely, hourly, daily, weekly, monthly

@app.task(minutely.before("45"))
def do_before():
    ...

@app.task(hourly.after("45:00"))
def do_after():
    ...

@app.task(daily.between("08:00", "14:00"))
def do_between():
    ...

@app.task(daily.at("11:00"))
def do_at():
    ...

@app.task(weekly.on("Monday"))
def do_on():
    ...

@app.task(monthly.starting("3rd"))
def do_starting():
    ...
