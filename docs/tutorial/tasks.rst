
 
Creating tasks
==============

 .. _creating-task:

Creating a tasks.yaml
---------------------

In this part we focus on creating tasks using 
``YAMLTaskLoader`` as that is the most convenient 
way to set up Red Engine. This loader reads and parses 
task configurations that are essentially list or dict 
of tasks including their initiation arguments. 

Examples of dict of task setups (keys are names of the tasks):

.. code-block:: yaml

    my-task-1:
        class: 'PyScript'
        ...

    my-task-2:
        class: 'PyScript'
        ...

Examples of list of task setups:

.. code-block:: yaml

    - class: 'PyScript'
      name: 'my-task-1'
      ...

    - class: 'PyScript'
      name: 'my-task-2'
      ...

When the ``YAMLTaskLoader`` parses a task configuration
YAML, the class is determined from the key ``class`` and
this class is initiated using the other parameters. For example,
in both of these files the "my-task-1" is initiated as 
``PyScript(name='my-task-1', ...)``. You can also set up all your
tasks in a single file or spread them to multiple.

Generally each task class has their own parameters and the 
parameters of the base class ():class:`redengine.core.Task`).
It is advisable to look up for the base class' parameters and 
the parameters of the task you are creating in order to set up 
as desired.


Setting Task Arguments
----------------------

:class:`redengine.core.Task` has numerous arguments but 
the most essential are:

- ``start_cond``: Specifies when the task may start running. See: :ref:`conditions-intro`
- ``end_cond``: Specifies when the task is terminated (if running and parallerized). See: :ref:`conditions-intro`
- ``execution``: How the task is executed. Allowed values:
    - ``'main'``: Runs on main thread and process,
    - ``'thread'``: Runs on another thread or
    - ``'process'``: Runs on another process.
- ``parameters``: Parameters passed for specifically to this task. This is a dictionary.


A more complete example of a task:

.. code-block:: yaml

    my-task-1:
        # Define which class is used
        class: 'PyScript'

        # Passed to Task (base class)
        start_cond: 'daily between 10:00 and 16:00 & time of week between Mon and Fri'
        execution: 'process'
        parameters: 
            data_source: 'Internet'

        # Passed to PyScript
        path: 'path/to/myfile.py'
        func: 'main'

    my-task-2:
        # Define which class is used
        class: 'CommandTask'

        # Passed to Task (base class)
        start_cond: "after task 'my-task-1' & weekly"
        end_cond: 'time of day between 23:00 and 06:00'
        execution: 'thread'

        # Passed to CommandTask
        command: 'python -m pip install redengine'

Built-in Tasks
==============

Possibly the most useful premade task class types are PyScript and CommandTask.
PyScript is useful to schedule and execute a function from a Python file while
CommandTask is useful for executing shell commands such as invoking programs 
written in different language.


PyScript (Python Script)
------------------------

Probably the most often used task type
is the :class:`redengine.tasks.PyScript`.
These are essentially Python files that 
have a given function which is executed
depending on the conditions.

Let's create file ``my_python_file.py``:

.. code-block:: python

    def main(my_session_arg, my_task_arg):
        ... # Do whatever your task is meant be done

Then a ``tasks.yaml``:

.. code-block:: yaml

    my-task:
        path: 'my_python_file.py'
        func: 'main'
        start_cond: 'daily between 09:00 and 15:00'
        parameters:
            my_task_arg: 'hello'
        
This task executes from file ``my_python_file.py`` the function 
``main(my_task_arg='hello')``.

See :class:`redengine.tasks.PyScript` for more options.


CommandTask (Terminal command)
------------------------------

CommandTask is simply a terminal command that is scheduled 
as a task. Note that it depends on the operating system and
available programs that one can do with this task type.

.. code-block:: yaml

    my-task:
        class: 'CommandTask'
        command: 'python -m pip install redengine'
        shell: false
        start_cond: 'daily between 09:00 and 15:00'

See :class:`redengine.tasks.CommandTask` for more options.