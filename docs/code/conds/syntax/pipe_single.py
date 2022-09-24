@app.task()
def do_things():
    ...

@app.task("after task 'do_things'")
def do_after_success():
    ...

@app.task("after task 'do_things' succeeded")
def do_after_success_2():
    ...

@app.task("after task 'do_things' failed")
def do_after_fail():
    ...

@app.task("after task 'do_things' finished")
def do_after_fail_or_success():
    ...
