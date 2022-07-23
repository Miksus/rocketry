from rocketry import Rocketry

app = Rocketry(config={"task_execution": "async"})

@app.task('every 20 seconds')
async def do_things():
    ...

@app.task('every 5 seconds')
async def do_stuff():
    ...

if __name__ == "__main__":
    app.run()