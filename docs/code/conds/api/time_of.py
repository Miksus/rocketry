from rocketry.conds import time_of_minute, time_of_hour, time_of_day, time_of_week

@app.task(time_of_minute.before("45"))
def do_constantly_minute_before():
    ...

@app.task(time_of_hour.after("45:00"))
def do_constantly_hour_after():
    ...

@app.task(time_of_day.between("08:00", "14:00"))
def do_constantly_day_between():
    ...

@app.task(time_of_week.on("Monday"))
def do_constantly_week_on():
    ...
