@app.task()
def do_a():
    ...

@app.task()
def do_b():
    ...


@app.task("after tasks 'do_a', 'do_b' succeeded")
def do_all_succeeded():
    ...

@app.task("after any tasks 'do_a', 'do_b' succeeded")
def do_any_succeeded():
    ...

@app.task("after any tasks 'do_a', 'do_b' failed")
def do_any_failed():
    ...

@app.task("after any tasks 'do_a', 'do_b' finished")
def do_any_failed_or_succeeded():
    ...
