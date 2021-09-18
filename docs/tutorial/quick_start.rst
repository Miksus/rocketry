Getting Started
===============

Install the package from Pip:

.. code-block:: console

    pip install redengine


Generate a quick setup to directory `myproject` that will get you started.

.. code-block:: console

   python -m redengine create myproject


This will create a project directory for your tasks. The structure is as follows:

| my_project/
| ├── tasks/
| │ ├── my_tasks-1/
| │ ├── ├── tasks.yaml
| │ ├── ├── task-1.py
| │ ├── ├── task-2.py
| │ ├── └── ...
| │ ├── extensions.yaml
| │ └── ...
| ├── conf.yaml
| ├── main.py
| └── models/
|    ├── conditions.py
|    ├── tasks.py
|    └── extensions.py


You can freely edit the files. In general:

- ``tasks/``: Put the tasks (for example Python scripts) here you wish to schedule.
- ``tasks/.../tasks.yaml``: This file configures how the tasks are scheduled and run. Fill in as needed. You can have as many of these as suitable.
- ``tasks/.../extensions.yaml``: This file configures extensions such as task pipelines. You can have multiple of these.
- ``conf.yaml``: Session configuration. 
- ``main.py``: Launcher for the scheduling session. Run this to start the scheduler.
- ``models/``: Put your extensions of Red Engine here.


Now you already have a working scheduler system. Just launch it:

.. code-block:: console

   python main.py

