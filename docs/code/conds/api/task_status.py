from rocketry.conds import finished, succeeded, failed

@app.task()
def do_things():
    ... # Dummy task for demonstration

@app.task(finished(task=do_things).this_hour)
def do_if_finish():
    ...

@app.task(succeeded(task=do_things).today.between("10:00", "12:00"))
def do_if_fail_between():
    ...

@app.task(failed.this_week.on("Monday"))
def do_if_itself_fails():
    ...
