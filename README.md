
# <span style="color:red">Red</span> Engine

> Advanced scheduling system for humans.

---

## What is it?
Red Engine is a Python package for scheduling scripts or functions. It is designed to be intuitive, 
expressive, extendable and production ready. 

## Core Features

- **Task:** a task can take various forms, for example:
    - a function,
    - a script or
    - create your own task class
- **Scheduling:** intuitive scheduling syntax.
    - All of these are valid instructions for scheduling a task:
        - `daily`
        - `every 10 minutes`
        - `weekly between Tuesday and Wednesday & after task 'another task'`
- **Parallerization:** Redengine supports many ways to execute a task: 
    - in another process,
    - in another thread or
    - in the main thread and process
- **Parametrization:** parametrize individual tasks or share them between the session. 
- **Easy start:** just install the package, use the premade configurations and work on your project.
- **Extendable:** everything is just a building block and the most is made to be modified. 

## Installation

- Clone the source code and pip install:
```shell
git clone https://github.com/Miksus/redengine.git
cd redengine
pip install .
```

## Getting Started

```shell
python -m redengine create myproject
```

---

## Author

* **Mikael Koli** - [Miksus](https://github.com/Miksus) - koli.mikael@gmail.com

