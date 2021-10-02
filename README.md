
# <span style="color:red">Red</span> Engine
> Advanced scheduling system.

-----------------

[![Documentation Status](https://readthedocs.org/projects/red-engine/badge/?version=latest)](https://red-engine.readthedocs.io/en/latest/?badge=latest)
[![Pypi version](https://badgen.net/pypi/v/redengine)](https://pypi.org/project/redengine/)
[![PyPI pyversions](https://badgen.net/pypi/python/redengine)](https://pypi.org/project/redengine/)

## What is it?
Red Engine is a Python scheduling library with a focus on productivity, readability and extendability.
It has powerful and intuitive scheduling syntax that is easy to extend with custom scheduling conditions. 
It allows various levels of parallelization and various ways to parametrize tasks. It is suitable 
for simple to moderately sized projects from process automatization to IOT.

Read more from the documentations: [Red Engine, documentations](https://red-engine.readthedocs.io/en/latest/)

## Core Features

- **Scheduling:** intuitive scheduling syntax.
    - All of these are valid instructions for scheduling a task:
        - `daily`
        - `every 2 hours, 10 minutes`
        - `weekly between Tuesday and Wednesday & after task 'another task'`
- **Parallelization:** run tasks in child processes or threads.
- **Parametrization:** parametrize individual tasks or share them between the session. 
- **Easy start:** just install the package, use the premade configurations and minimize boilerplate.
- **Extendable:** everything is just a building block and the most is made to be modified. 

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

