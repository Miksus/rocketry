

<h1 align="center"><a href="https://rocketry.readthedocs.io">Rocketry</a></h1>
<p align="center">
    <em>The engine to power your Python apps</em>
</p>
<p align="center">
    <a href="https://github.com/Miksus/rocketry/actions/workflows/main.yml/badge.svg?branch=master" target="_blank">
        <img src="https://github.com/Miksus/rocketry/actions/workflows/main.yml/badge.svg?branch=master" alt="Test">
    </a>
    <a href="https://codecov.io/gh/Miksus/rocketry" target="_blank">
        <img src="https://codecov.io/gh/Miksus/rocketry/branch/master/graph/badge.svg?token=U2KF1QA5HT" alt="Test coverage">
    </a>
    <a href="https://pypi.org/project/rocketry" target="_blank">
        <img src="https://badgen.net/pypi/v/rocketry?color=969696" alt="Package version">
    </a>
    <a href="https://pypi.org/project/rocketry" target="_blank">
        <img src="https://badgen.net/pypi/python/rocketry?color=969696&labelColor=black" alt="Supported Python versions">
    </a>
</p>

-----------------

## What is it?

Rocketry is a modern statement-based scheduling framework 
for Python. It is simple, clean and extensive.
It is suitable for small and big projects.

This is how it looks like:

```python
from rocketry import Rocketry
from rocketry.conds import daily

app = Rocketry()

@app.task(daily)
def do_daily():
    ...

if __name__ == '__main__':
    app.run()
```

Core functionalities:

- Powerful scheduling
- Concurrency (async, threading, multiprocess)
- Parametrization
- Task pipelining
- Modifiable session also in runtime
- Async support

Links:

- Documentation: https://rocketry.readthedocs.io
- Source code: https://github.com/Miksus/rocketry
- Releases: https://pypi.org/project/rocketry/

## Why Rocketry?

Unlike the alternatives, Rocketry's scheduler is 
statement-based. Rocketry natively supports the 
same scheduling strategies as the other options, 
including cron and task pipelining, but it can also be
arbitrarily extended using custom scheduling statements.

Here is an example of custom conditions:

```python
from rocketry.conds import daily, time_of_week
from pathlib import Path

@app.cond()
def file_exists(file):
    return Path(file).exists()

@app.task(daily.after("08:00") & file_exists("myfile.csv"))
def do_work():
    ...
```

Rocketry is suitable for quick automation projects
and for larger scale applications. It does not make
assumptions of your project structure.

## Installation

Install Rocketry from [PyPI](https://pypi.org/project/rocketry/):

```shell
pip install rocketry
```


## More Examples

Here are some more examples of what it can do.

**Scheduling:**

```python
from rocketry.conds import every
from rocketry.conds import hourly, daily, weekly, 
from rocketry.conds import time_of_day
from rocketry.conds import cron

@app.task(every("10 seconds"))
def do_continuously():
    ...

@app.task(daily.after("07:00"))
def do_daily_after_seven():
    ...

@app.task(hourly & time_of_day.between("22:00", "06:00"))
def do_hourly_at_night():
    ...

@app.task((weekly.on("Mon") | weekly.on("Sat")) & time_of_day.after("10:00"))
def do_twice_a_week_after_ten():
    ...

@app.task(cron("* 2 * * *"))
def do_based_on_cron():
    ...
```

**Pipelining tasks:**

```python
from rocketry.conds import daily, after_success
from rocketry.args import Return

@app.task(daily.after("07:00"))
def do_first():
    ...
    return 'Hello World'

@app.task(after_success(do_first))
def do_second(arg=Return('do_first')):
    # arg contains the value of the task do_first's return
    ...
    return 'Hello Python'
```


**Parallelizing tasks:**

```python
from rocketry.conds import daily

@app.task(daily, execution="main")
def do_unparallel():
    ...

@app.task(daily, execution="async")
async def do_async():
    ...

@app.task(daily, execution="thread")
def do_on_separate_thread():
    ...

@app.task(daily, execution="process")
def do_on_separate_process():
    ...
```

---

## Interested?

Read more from [the documentation](https://rocketry.readthedocs.io).

## About Library

- **Author:** Mikael Koli ([Miksus](https://github.com/Miksus)) - koli.mikael@gmail.com
- **License:** MIT

