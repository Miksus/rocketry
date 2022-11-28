from rocketry import Rocketry
from rocketry.args import Arg, FuncArg, Return

app = Rocketry()
app.params(my_arg='hello')

@app.task("every 10 seconds")
def do_things(arg=Arg('my_arg')):

    # Argument 'arg' has value 'hello'
    assert arg == 'hello'
    return 'stuff'

@app.task("after task 'do_things'")
def do_with_return(arg=Return('do_things')):

    # Argument 'arg' is the return value of the task 'do_things'
    assert arg == 'stuff'

@app.task("after task 'do_things'")
def do_with_funcarg(arg=FuncArg(lambda: 'hello world')):

    # Argument 'arg' is the return value of the task 'do_things'
    assert arg == 'stuff'

if __name__ == "__main__":
    app.run()
