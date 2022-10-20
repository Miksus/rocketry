from rocketry.conds import running

@app.task(end_cond=running.more_than("2 mins"))
def do_things():
    ... # Terminates if runs over 2 minutes

@app.task(running(do_things))
def do_if_runs():
    ... # Starts if do_things is running

@app.task(running(do_things).less_than("2 mins"))
def do_if_runs_less_than():
    ... # Starts if do_things is running less than 2 mins

@app.task(running(do_things).between("2 mins", "5 mins"))
def do_if_runs_between():
    ...
    # Starts if do_things is running
    # less than 2 mins but no more than 5 minutes
