
# <span style="color:red">Red</span> Engine
> Advanced scheduling system.

-----------------

[![Pypi version](https://badgen.net/pypi/v/redengine)](https://pypi.org/project/redengine/)
[![build](https://github.com/Miksus/red-engine/actions/workflows/main.yml/badge.svg?branch=master)](https://github.com/Miksus/red-engine/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/Miksus/red-engine/branch/master/graph/badge.svg?token=U2KF1QA5HT)](https://codecov.io/gh/Miksus/red-engine)
[![Documentation Status](https://readthedocs.org/projects/red-engine/badge/?version=latest)](https://red-engine.readthedocs.io/en/latest/?badge=latest)
[![PyPI pyversions](https://badgen.net/pypi/python/redengine)](https://pypi.org/project/redengine/)

## What is it?
Red Engine is a Python scheduling library with a focus on productivity, readability and extendability.
It has powerful and intuitive scheduling syntax that is easy to extend with custom conditions. 
The sysystem allows various levels of parallelization and various ways to parametrize tasks. It is suitable 
for simple to larger projects from process automatization to IOT.

Read more from the documentations: [Red Engine, documentations](https://red-engine.readthedocs.io/en/stable/)

## Core Features

- **Scheduling:** intuitive and powerful scheduling syntax.
- **Parallelization:** run tasks on child processes or threads.
- **Parametrization:** parametrize individual tasks and pass return values as inputs to next. 
- **Easy start:** just install the package, use the premade configurations and work on your problem.
- **Extendable:** everything is just a building block designed for modifications. 

## Installation

```shell
pip install redengine
```

## How it looks like

> Minimal example

```python
from redengine.tasks import FuncTask
from redengine import Session

session = Session()

@FuncTask(start_cond="daily")
def my_task_1():
    ... # Do whatever.

@FuncTask(start_cond="every 10 min")
def my_task_2():
    ... # Do whatever.

# Start scheduling
session.start()
```


> Customize

```python
import os, re

from redengine.tasks import FuncTask
from redengine.conditions import FuncCond
from redengine import Session

session = Session()

# Custom conditions
@FuncCond(syntax="is work time")
def is_work_time():
    # This custom condition is
    # directly usable in parsing
    return True

@FuncCond(syntax=re.compile("file (?P<filename>.+) exists"))
def file_exists(filename):
    # You can also use regex in custom conditions.
    # The pattern is matched and named groups are 
    # passed as parameters to the function
    return os.path.exists(filename)

# Tasks
@FuncTask(start_cond="is work time & file C:/Temp/mydata.csv exists")
def do_work():
    # Runs when is_work_time is True 
    # and file 'C:/Temp/mydata.csv' exists
    ... 

# Start scheduling
session.start()
```


> Pipeline tasks and their outputs

```python
from redengine.tasks import FuncTask
from redengine.conditions import FuncCond
from redengine.arguments import Return
from redengine import Session

session = Session()

@FuncTask(start_cond="daily")
def first_task():
    ... # Run once a day
    return some_data

@FuncTask(start_cond="after task 'first_task'", parameters={'mydata': Return('first_task')})
def second_task(mydata):
    ... # Runs after first_task and "mydata" is the output of first_task
    return some_data

@FuncTask(
    start_cond="after task 'first_task' & after task 'second_task'", 
    parameters={'mydata1': Return('first_task'), "mydata2": Return('second_task')}
)
def third_task(mydata1, mydata2):
    # Runs after first_task and second_task
    # and pass arguments as defined in parameters
    ... 
    return some_data

# Start scheduling
session.start()
```


> Parallelize tasks

```python
from redengine.tasks import FuncTask
from redengine.conditions import FuncCond
from redengine.arguments import Return
from redengine import Session

session = Session()

@FuncTask(execution="main")
def run_on_main():
    ... # Runs on main thread and process

@FuncTask(execution="thread")
def run_on_thread():
    ... # Runs on a separate thread

@FuncTask(execution="process")
def run_on_process():
    ... # Runs on a separate process

# Start scheduling
session.start()
```


> Do complex scheduling

```python
from redengine.tasks import FuncTask
from redengine.conditions import FuncCond
from redengine.arguments import Return
from redengine import Session

session = Session()

@FuncTask(start_cond="daily after 10:00")
def run_daily():
    ... # Runs once a day after 10 AM

@FuncTask(start_cond="daily between 08:00 and 10:00 | daily between 18:00 and 22:00")
def run_twice_a_day():
    # Runs twice a day
    # First from 8 AM to 10 AM 
    # and then from 6 PM to 10 PM
    ...

@FuncTask(start_cond="daily & time of week between Monday and Friday")
def run_daily_on_weekdays():
    # Runs once a day but only on week days. 
    ...

@FuncTask(start_cond="""after task 'run_daily' 
                        & time of day between 08:00 and 17:00
                        & ~has failed today""")
def run_complex():
    # Runs after run_daily but only between 8 AM and 5 PM
    # and only if the task itself has not failed today
    ...

# Start scheduling
session.start()
```

---

## Author

* **Mikael Koli** - [Miksus](https://github.com/Miksus) - koli.mikael@gmail.com

