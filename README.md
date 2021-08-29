
# Powerbase

> Advanced scheduling system for humans.

---

## What is it?
Powerbase is a Python package for scheduling scripts or functions. It is designed to be intuitive, 
expressive and extendable. 

## Core Features

- **Task:** a task can take various forms, for example:
    - a function,
    - a script,
    - a Jupyter notebook or
    - create your own task class
- **Scheduling:** Powerbase has intuitive scheduling syntax and lower level object oriented scheduling.
    - All of these are valid instructions for scheduling a task:
        - `daily`
        - `every 10 minutes`
        - `weekly between Tuesday and Wednesday & after task 'another task'`
- **Parallerization:** Powerbase supports many ways to execute a task: 
    - in another process,
    - in another thread or
    - in the main thread and process
- **Parametrization:** parametrize individual tasks or share them between the session. 
- **Intuitive:** just install the package, use the premade configurations and work on your project.
- **Extendable:** everything is just a building block and almost everything is made to be modified. 

## Installation

- Clone the source code and pip install:
```shell
git clone https://github.com/Miksus/powerbase.git
cd powerbase
pip install -e .
```

## Example

### High level example

1. Create a folder
2. Create a subfolder 'mytasks' and put some task files there:
    - mytasks/scrape/wiki.py
        ```python
        def fetch_article(url):
            ...
        ```
    - mytasks/fetch_random.yaml
        ```yaml
        name: fetch_random_article
        path: scrape/wiki.py
        func: fetch_article
        parameters:
            url: 'https://en.wikipedia.org/wiki/Special:Random'
        ```
3. Add scheduling script 'main.py'
    ```python
    from powerbase import session
    session.set_scheme("pyproject")
    session.set_scheme("csv_logging")
    session.config["tasks_from_path"] = "mytasks/"
    session.start()
    ```
4. Run 'main.py'

## Low level example

```python
from powerbase import Session, Scheduler
from powerbase.tasks import FuncTask
from powerbase.conditions import DependSuccess, TaskExecutable
from powerbase.time import TimeOfDay, TimeOfWeek

def do_stuff(arg1, arg2):
    ...

def do_other_stuff(arg1, arg2):
    ...

# Create session
session = Session(parameters={"arg1": "something"})

# Create some tasks
FuncTask(
    do_stuff, 
    start_cond=TaskExecutable(period=TimeOfDay("10:00", "14:00")), 
    parameters={"arg2": "other"},
    name="mytask-1"
)
FuncTask(
    do_other_stuff, 
    start_cond=DependSuccess(depend_task="mytask-1") & TaskExecutable(period=TimeOfWeek("Mon", "Fri")), 
    name="mytask-2"
)

# Start the session
session.start()
```

---

## Test
Pytest was chosen as testing suites. Tests are found in test directory inside the source. 


---

## Author

* **Mikael Koli** - [Miksus](https://github.com/Miksus) - koli.mikael@gmail.com

