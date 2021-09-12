Creating tasks
==============

PyScript (Python Script)
------------------------

Probably the most often used task type
is the :class:`redengine.tasks.PyScript`.
These are essentially Python files that 
contain a given function which is executed
depending on the conditions.

Let's create file ``my_python_file.py``:

.. code-block:: python

    def main(my_session_arg, my_task_arg):
        ... # Do whatever your task is meant be done

Then if you are using ``YAMLTaskLoader``, add a ``tasks.yaml``
file to the tasks folder.

.. code-block:: yaml

    # Either dict of tasks (key is the name of the task) 
    # or list of tasks 
    my-task:
        # PyScript task that executes function 'main'
        # from task-1.py (relative to where conftask.yaml is)
        path: 'my_python_file.py' # Where the py file is relative to this file
        func: 'main'
        parameters:
            my_task_arg: 'hello'

        # Runs once a day between 9 AM and 3 PM
        start_cond: 'daily between 09:00 and 15:00'