from rocketry.conds import daily, after_success
from rocketry.args import Return

@app.task(daily)
def do_first():
    ...
    return 'Hello World'

@app.task(after_success(do_first))
def do_second(arg=Return(do_first)):
    # arg's value is "Hello World"
    ...