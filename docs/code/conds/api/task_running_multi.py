from rocketry.conds import running

@app.task(running <= 4, multilanch=True)
def do_parallel_limited():
    ... # Allows 4 parallel runs 

@app.task(~running, multilanch=True)
def do_non_parallel():
    ... # Allows no parallel runs

@app.task(running(do_parallel_limited) >= 2)
def do_if_runs_parallel():
    ... # Runs if the other has at least two parallel runs