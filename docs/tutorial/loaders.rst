.. _loaders:

Loaders
=======

Loaders are tasks that have special purpose:
they load tasks, extensions and session 
settings from different files to the session. These 
are especially useful to reduce boilerplate
in importing all the tasks and extensions 
the scheduling system uses.

Essentially loaders are meta tasks.
They don't support parallerization via ``process``
and should always be run as setup tasks.

There are several prebuilt loaders:

- ``PyLoader``: Simply imports all the matched Python files.
- ``TaskLoader``: Loads task configuration files that specify list of tasks.
- ``ExtensionLoader``: Loads extensions from configuration files.
- ``SessionLoader``: Loads session configuration files and append them to current session.

Currently ``TaskLoader``, ``ExtensionLoader`` and ``SessionLoader`` support
only YAML configuration files.

You can set the desired loader(s) to the 
session configuration file that is read using
``Session.from_dict``:

.. code-block:: yaml

    ...
    tasks:
      - class: PyLoader
        path: 'tasks/'
        glob: '**/tasks.py'
        on_startup: True
      - class: TaskLoader
        path: 'tasks/'
        glob: '**/tasks.yaml'
        on_startup: True
      - class: ExtensionLoader
        path: 'tasks/'
        glob: '**/extensions.yaml'
        on_startup: True
    ...

The ``path`` is the directory that the files are looked 
from and ``glob`` is the file pattern which the configuration
files must match. If it does not match, it's not included.

You can also set the loaders in Python code:

.. code-block:: python

    from redengine.tasks.loaders import Pyloader, TaskLoader, ExtensionLoader

    Pyloader(path="tasks/", glob="**/tasks.py")
    TaskLoader(path="tasks/", glob="**/tasks.yaml")
    ExtensionLoader(path="tasks/", glob="**/extensions.yaml")

What next? 
----------

Put your tasks to the ``tasks/`` directory. 
For example, for ``PyLoader`` create a ``tasks.py``
somewhere to the directory that contains the 
objects you wish to create, like:

.. code-block:: python

    from redengine.tasks import FuncTask

    @FuncTask(name="my_task", start_cond="daily")
    def do_things():
        ...

Or for ``TaskLoader``, create a ``task.yaml`` somewhere
in the directory:

.. code-block:: yaml

    my_task:
        path: 'funcs.py'
        func: 'main'
        start_cond: 'daily'

Or for ``ExtensionLoader``, create a ``extension.yaml`` somewhere
in the directory:

.. code-block:: yaml

    sequences:
        tasks:
            - 'my_task_1'
            - 'my_task_2'
        interval: 'every 2 hours'