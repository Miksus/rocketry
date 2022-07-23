
Scheduler with API (FastAPI)
============================

This is an example to integrate FastAPI with Rocketry.
Copy the files to your project and modify as you need.

This example contains three files:

- **scheduler.py**: Rocketry app. Put your tasks here.
- **api.py**: FastAPI app. Contains the API routes.
- **main.py**: Combines the apps. Run this file.

**scheduler.py**

.. literalinclude:: /code/demos/fast_api/scheduler.py
    :language: py

**ui.py**

.. literalinclude:: /code/demos/fast_api/api.py
    :language: py

**main.py**

.. literalinclude:: /code/demos/fast_api/main.py
    :language: py

The system works via *async*. The execution alters between
the API and the scheduler constantly.

.. note::

    Uvicorn modifies signal handlers. In order to make ``keyboardinterrupt``
    to shut down the scheduler as well, we have to modify Uvicorn server. 
