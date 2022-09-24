from rocketry.conds import running

@app.task(end_cond=running(more_than="2 minutes"))
def do_things():
    ... # Terminates if runs over 2 minutes

@app.task(start_cond=running(do_things))
def do_if_runs():
    ... # Starts if do_things is running

@app.task(start_cond=running(do_things, less_than="2 minutes"))
def do_if_runs_less_than():
    ... # Starts if do_things is running less than 2 mins
