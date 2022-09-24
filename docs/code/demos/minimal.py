from rocketry import Rocketry

app = Rocketry()

@app.task('daily')
def do_things():
    ...

if __name__ == "__main__":
    app.run()
