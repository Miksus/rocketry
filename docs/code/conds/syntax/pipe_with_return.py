from rocketry.args import Return

@app.task("daily")
def do_first():
    ...
    return 'Hello World'

@app.task("after task 'do_first'")
def do_second(arg=Return('do_first')):
    # arg's value is "Hello World"
    ...
