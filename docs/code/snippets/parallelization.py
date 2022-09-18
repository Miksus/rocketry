@app.task(execution="main")
def do_unparallel():
    ...

@app.task(execution="async")
async def do_unparallel():
    ...

@app.task(execution="thread")
def do_on_separate_thread():
    ...

@app.task(execution="process")
def do_on_separate_process():
    ...