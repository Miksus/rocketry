from rocketry import Rocketry

app = Rocketry()

@app.task('daily')
def do_things():
    ...

@app.task("after task 'do_things'")
def do_after_things():
    ...

if __name__ == "__main__":
    app.run()
