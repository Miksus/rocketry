
Scheduler with an API
=====================

This example shows a simple scheduler that has FastAPI integrated
on runtime. The FastAPI app is able to read Red Engine app's logs,
tasks, create tasks, modify tasks, delete tasks or shut down the 
scheduling session.

This example contains two files:

- ``api.py``: FastAPI application
- ``scheduler.py``: Red Engine application

**api.py**

.. literalinclude:: /code/examples/scheduler_with_api/api.py
    :language: py

**scheduler.py**

.. literalinclude:: /code/examples/scheduler_with_api/scheduler.py
    :language: py

.. note::

    Run the ``scheduler.py``. Remember to have both on the 
    same directory.

Read more about FastAPI: `FastAPI docs <https://fastapi.tiangolo.com/>`_