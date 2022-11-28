from rocketry.conds import (after_all_success, after_any_fail,
                            after_any_finish, after_any_success)


@app.task()
def do_a():
    ...

@app.task()
def do_b():
    ...


@app.task(after_all_success(do_a, do_b))
def do_all_succeeded():
    ...

@app.task(after_any_success(do_a, do_b))
def do_any_succeeded():
    ...

@app.task(after_any_fail(do_a, do_b))
def do_any_failed():
    ...

@app.task(after_any_finish(do_a, do_b))
def do_any_failed_or_succeeded():
    ...
