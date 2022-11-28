from rocketry.args import Return
from rocketry.conds import after_success, daily


@app.task(daily)
def do_first():
    return 'Hello World'

@app.task(after_success(do_first))
def do_second(arg=Return(do_first)):
    # arg's value is "Hello World"
    ...
