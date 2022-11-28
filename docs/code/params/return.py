from rocketry.args import Return


@app.task()
def do_first():

    return 'Hello World'

@app.task()
def do_second(arg=Return(do_first)):
    # arg's value is "Hello World"
    ...
