
# <span style="color:red">Red</span> Engine
> Advanced scheduling system.

-----------------

[![Pypi version](https://badgen.net/pypi/v/redengine)](https://pypi.org/project/redengine/)
[![build](https://github.com/Miksus/red-engine/actions/workflows/main.yml/badge.svg?branch=master)](https://github.com/Miksus/red-engine/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/Miksus/red-engine/branch/master/graph/badge.svg?token=U2KF1QA5HT)](https://codecov.io/gh/Miksus/red-engine)
[![Documentation Status](https://readthedocs.org/projects/red-engine/badge/?version=latest)](https://red-engine.readthedocs.io/en/latest/?badge=latest)
[![PyPI pyversions](https://badgen.net/pypi/python/redengine)](https://pypi.org/project/redengine/)

## What is it?

Red Engine is an advanced open source scheduling library 
with a focus on productivity, readability and extendability. 
It works well in orchestrating task execution in a complex system
or as a tool for quick and simple automation. Example use cases for the 
framework include orchestrating ETL pipelines, scheduling web scrapers
or algorithms, building IOT applications or automating daily tasks.

The library is pure Python with minimal dependencies. It is 
pythonic and the style is similar to other notable frameworks
in Python ecosystem. 

Read more from the documentations: [Red Engine, documentations](https://red-engine.readthedocs.io/en/stable/)

## Why Red Engine?

Most of the candidates for scheduling framework tend to be 
either complex to configure or too simple for advanced use. Red Engine
aims to handle both sides of the spectrum without sacrificing from the other. 
It only takes a minute to set it up and schedule some tasks but there are 
a lot of advanced features such as parametrization, parallelization, 
pipelining, runtime APIs and logging provided straight out of the box. 
The library is also created in mind of extending and customization.

Red Engine is reliable and well tested. You can build your project
around Red Engine or simply embed it to an existing project. 

## Core Features

- **Scheduling syntax:** intuitive and very powerful scheduling syntax
- **Parallelization:** run tasks simultaneously on separate processes or threads
- **Parametrization:** parametrize individual tasks and pipeline return values
- **Extendable:** almost everything is designed for modifications

## Additional Features

- **APIs:** Communicate with your scheduler real time using HTTP requests
- **Dependencies:** view your task dependencies as a graph
- **Easy setup:** use the premade configurations and get started immediately
- **Logging:** Red Engine simply extends logging library making task logging trivial
- **Built-ins:** There are a lot of pre-built conditions for various purposes out of the box

## Installation

Red Engine can be installed from [Pypi](https://pypi.org/project/redengine/):

```shell
pip install redengine
```

## How it looks like

Minimal example:

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

## More Examples

Parallelize tasks:

```python
@FuncTask(execution="main")
def run_on_main():
    ... # Runs on main thread and process

@FuncTask(execution="thread")
def run_on_thread():
    ... # Runs on a separate thread

@FuncTask(execution="process")
def run_on_process():
    ... # Runs on a separate process
```

Pipeline tasks and their outputs:

```python
from redengine.arguments import Return
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
```

Create custom condition components:

```python
from redengine.conditions import FuncCond

@FuncCond(syntax="is work time")
def is_work_time():
    # This custom condition is
    # directly usable in parsing
    ...
    return True

# An example task
@FuncTask(start_cond="daily & is work time")
def do_work():
    # Runs once a day when is_work_time is True 
    ... 

```

Do complex scheduling:

```python
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
```

---

## Author

* **Mikael Koli** - [Miksus](https://github.com/Miksus) - koli.mikael@gmail.com

