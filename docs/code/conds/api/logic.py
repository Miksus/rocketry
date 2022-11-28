from rocketry.conds import false, true


@app.task(true)
def do_constantly():
    ...

@app.task(false)
def do_never():
    ...

@app.task(true & false)
def do_and():
    ...

@app.task(true | false)
def do_or():
    ...

@app.task(~false)
def do_not():
    ...

@app.task((true | false) & ~(true | false))
def do_nested():
    ...
