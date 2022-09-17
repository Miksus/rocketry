
Rocketry VS Alternatives
========================

There are other alternatives for scheduling as well.
This section contains comparisons between Rocketry
and other scheduling tools.

Features unique for **Rocketry**:

- **Statement-based scheduling**: Rocketry's condition system is unique and it is 
  simple to use, elegant and easy to extend. It is capable of addressing more complex
  scheduling needs than the standard scheduling paradigm.
- **Time periods**: Rocketry has sophisticated and robust time 
  period system.
- **Parametrization**: Rocketry's parameter system enables passing
  the output of a task as the input for another task.
- **No assumptions**: The framework does not dictate how to structure
  your project or how to use the framework. The log records can be 
  directed anywhere, the framework can be integrated with other frameworks
  and you decide how you form the tasks.


Rocketry vs Crontab
-------------------

Crontab is a scheduler for Unix-like operating systems.
It is light weight and it is able to run tasks (or jobs) 
periodically, ie. hourly, weekly or on fixed dates.

When **Rocketry** might be a better choice:

- You are building a system and not just running individual scripts 
- You need task pipelining
- You need more complex and custom scheduling 
- You are not familiar Unix-Linux
- You work with Windows

When **Crontab** might be a better choice:

- If you need a truly light weight solution
- You are not familiar with Python
- You only want to run scripts independently at given periods

.. note::

    Rocketry also has fully functioning cron condition.

Rocketry vs APScheduler
------------------------

APScheduler is a relatively simple scheduler library for Python.
It provides Cron-style scheduling and some interval based scheduling.

When **Rocketry** might be a better choice:

- You are building an automation system
- You need more complex and customized scheduling
- You need to pipeline tasks 

When **APScheduler** might be a better choice:

- You wish to have the tasks stored in a database (and not in Python code)

.. note::

    In Rocketry, you could make a startup task that generates the rest of the 
    tasks from a database as well.

Rocketry vs Celery
------------------

Celery is a task queue system meant for distributed execution and 
scheduling background tasks for web back-ends.

When **Rocketry** might be a better choice:

- You are building an automation system
- You need more complex and customized scheduling
- You work with Windows

When **Celery** might be a better choice:

- You are running background tasks for web servers
- You need higher performance
- You need distributed execution

.. note::

    Celery works via task queues but such mechanism could be implemented
    to Rocketry as well by creating a condition that is true only for the
    task next in the queue and false for others. Then when the first task
    in the queue has been started, it is dropped from the queue.

Rocketry vs Airflow
-------------------

Airflow is a a workflow management system used heavily
in data pipelines. It has a scheduler and a built-in monitor.

When **Rocketry** might be a better choice:

- You need more complex scheduling
- You work with Windows
- You need something that is easy to set up
  and quick to get produtive with
- You are building an application
- You want more customization

When **Airflow** might be a better choice:

- You are building standard data pipelines
- You would like to have more out-of-the-box
- You need distributed execution
- You work in data engineering


.. note::

    Rocketry handles time-related scheduling, task pipelining
    and custom scheduling via the same condition mechanism.
    Airflow implements these via separate concepts: schedulers,
    pipelines and sensors.