@app.task(execution="main")
def do_main():
    ...

@app.task(execution="async")
async def do_async():
    ...

@app.task(execution="thread")
def do_thread():
    ...

@app.task(execution="process")
def do_process():
    ...
