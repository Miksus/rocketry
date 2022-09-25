@app.task('every 10 seconds')
def do_constantly():
    ...

@app.task('hourly')
def do_hourly():
    ...

@app.task('daily between 08:00 and 14:00')
def do_daily():
    ...

@app.task("after task 'do_daily'")
def do_after():
    ...

@app.task('true & false & ~(true | false)')
def do_logic():
    ...
