
# Rocketry
> Powering your Python Apps

-----------------

[![Pypi version](https://badgen.net/pypi/v/rocketry)](https://pypi.org/project/rocketry/)
[![build](https://github.com/Miksus/rocketry/actions/workflows/main.yml/badge.svg?branch=master)](https://github.com/Miksus/rocketry/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/Miksus/rocketry/branch/master/graph/badge.svg?token=U2KF1QA5HT)](https://codecov.io/gh/Miksus/rocketry)
[![Documentation Status](https://readthedocs.org/projects/rocketry/badge/?version=latest)](https://rocketry.readthedocs.io/en/latest/?badge=latest)
[![PyPI pyversions](https://badgen.net/pypi/python/rocketry)](https://pypi.org/project/rocketry/)

## What is it?

Rocketry is a modern scheduling framework for Python 
applications. It is simple, clean and extensive. It is 
the engine that sets your Python programs alive.

The library is minimal on the surface but extensive 
and customizable underneath. The syntax very clean:

```python
from rocketry import Rocketry

app = Rocketry()

@app.task('daily')
def do_daily():
    ...

if __name__ == '__main__':
    app.run()
```

Compared to alternatives, Rocketry has perhaps the most elegant syntax and is the most productive. It offers more features than Crontab or APScheduler but is much
easier to work with than Airflow. It does not make assumptions of your project.

Read more from the documentations: [Rocketry, documentations](https://rocketry.readthedocs.io/en/stable/)

## Installation

Install Rocketry from [PyPI](https://pypi.org/project/rocketry/):

```shell
pip install rocketry
```


## More Examples?

**Scheduling:**

```python
@app.task("every 10 seconds")
def do_continuously():
    ...

@app.task("daily after 07:00")
def do_daily_after_seven():
    ...

@app.task("hourly & time of day between 22:00 and 06:00")
def do_hourly_at_night():
    ...

@app.task("(weekly on Monday | weekly on Saturday) & time of day after 10:00")
def do_twice_a_week_after_ten():
    ...
```

**Pipelining tasks:**

```python
from rocketry.args import Return

@app.task("daily after 07:00")
def do_first():
    ...
    return 'Hello World'

@app.task("after task 'do_first'")
def do_second(arg=Return('do_first')):
    # arg contains the value of the task do_first's return
    ...
    return 'Hello Python'
```

**Parallelizing tasks:**

```python
@app.task("daily", execution="main")
def do_unparallel():
    ...

@app.task("daily", execution="thread")
def do_on_separate_thread():
    ...

@app.task("daily", execution="process")
def do_on_separate_process():
    ...
```

---

## Author

* **Mikael Koli** - [Miksus](https://github.com/Miksus) - koli.mikael@gmail.com

