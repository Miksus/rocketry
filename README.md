

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

Rocketry is a modern scheduling framework for Python 
applications. It is simple, clean and extensive. It is 
the automation engine that sets your Python programs alive.

The library is minimal on the surface but large 
and highly customizable underneath. The syntax very clean:

```python
from rocketry import Rocketry

app = Rocketry()

@app.task('daily')
def do_daily():
    ...

if __name__ == '__main__':
    app.run()
```

<details markdown="1">
<summary>Dislike the string syntax?</summary>

There is also a condition API which is almost
identical to the string syntax:

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

</details>


Compared to alternatives, Rocketry has the most elegant syntax and is the most productive. 
It offers more features than Crontab or APScheduler but is much
easier to work with than Airflow. It does not make assumptions of your project.

Core functionalities:

- Powerful scheduling syntax
- A lot of built-in scheduling options
- Task parallelization
- Task parametrization
- Task pipelining
- Modifiable session also in runtime
- Async support

Links:

- Documentation: https://rocketry.readthedocs.io
- Source code: https://github.com/Miksus/rocketry
- Releases: https://pypi.org/project/rocketry/

## Installation

Install Rocketry from [PyPI](https://pypi.org/project/rocketry/):

```shell
pip install rocketry
```


## More Examples

Here are some more examples of what it can do.

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
<details markdown="1">
<summary>Same with condition API</summary>

```python
from rocketry.conds import every, daily, hourly, time_of_day, weekly

@app.task(every("10 seconds"))
def do_continuously():
    ...

@app.task(daily.after("07:00"))
def do_daily_after_seven():
    ...

@app.task(hourly & time_of_day.between("22:00", "06:00"))
def do_hourly_at_night():
    ...

@app.task((weekly.on("Monday") | weekly.on("Saturday")) & time_of_day.after("10:00"))
def do_twice_a_week_after_ten():
    ...
```

</details>


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
<details markdown="1">
<summary>Same with condition API</summary>

```python
from rocketry.conds import daily, after_success
from rocketry.args import Return

@app.task(daily.after("07:00"))
def do_first():
    ...
    return 'Hello World'

@app.task(after_success(do_first))
def do_second(arg=Return(do_first)):
    # arg contains the value of the task do_first's return
    ...
    return 'Hello Python'
```

</details>


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

## Interested?

Read more from [the documentation](https://rocketry.readthedocs.io).

## About Library

- **Author:** Mikael Koli ([Miksus](https://github.com/Miksus)) - koli.mikael@gmail.com
- **License:** MIT

