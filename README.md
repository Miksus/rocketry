
# <span style="color:red">Red</span> Engine
> Advanced scheduling system.

-----------------

[![Documentation Status](https://readthedocs.org/projects/red-engine/badge/?version=latest)](https://red-engine.readthedocs.io/en/latest/?badge=latest)
[![Pypi version](https://badgen.net/pypi/v/redengine)](https://pypi.org/project/redengine/)
[![PyPI pyversions](https://badgen.net/pypi/python/redengine)](https://pypi.org/project/redengine/)

## What is it?
Red Engine is a Python scheduling library with a focus on productivity, readability and extendability.
It has powerful and intuitive scheduling syntax that is easy to extend with custom conditions. 
The sysystem allows various levels of parallelization and various ways to parametrize tasks. It is suitable 
for simple to larger projects from process automatization to IOT.

Read more from the documentations: [Red Engine, documentations](https://red-engine.readthedocs.io/en/stable/)

## Core Features

- **Scheduling:** intuitive and powerful scheduling syntax.
    - All of these are valid instructions for scheduling a task:
        - `daily`
        - `every 2 hours, 10 minutes`
        - `weekly between Tuesday and Wednesday & after task 'another task'`
- **Parallelization:** run tasks in child processes or threads.
- **Parametrization:** parametrize individual tasks or share them inside a session. 
- **Easy start:** just install the package, use the premade configurations and get to it.
- **Extendable:** everything is just a building block designed for modifications. 

## Installation

```shell
pip install redengine
```

## How it looks like

```python
from redengine.tasks import FuncTask
from redengine import Session

session = Session()

@FuncTask(start_cond="daily between 10:00 and 15:00")
def my_task_1():
    ... # Do whatever.

@FuncTask(start_cond="after task 'my_task_1'")
def my_task_2():
    ... # Do whatever.

# Start scheduling
session.start()
```

---

## Author

* **Mikael Koli** - [Miksus](https://github.com/Miksus) - koli.mikael@gmail.com

