from rocketry.conds import after_success, after_fail, after_finish

@app.task()
def do_things():
    ...

@app.task(after_success(do_things))
def do_after_success():
    ...

@app.task(after_fail(do_things))
def do_after_fail():
    ...

@app.task(after_finish(do_things))
def do_after_fail_or_success():
    ...
