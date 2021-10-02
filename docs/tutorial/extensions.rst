Extensions
==========

Extensions are additional components that 
change the behaviour of tasks or their 
conditions. Perhaps the most useful components
are task pipelines which forces the given tasks
to execute one after another. 

Currently there is only one extension: 
:class:`redengine.ext.Sequence`.

Sequence
--------

Sequences are task pipelines that execute the listed
tasks one by one. If interval is given, the sequence
starts when the current time is in the interval and 
will execute until either the sequence is completed
or the current time no longer is in the interval.
If no interval is given, the sequence will execute 
till the last task in the sequence and then will 
restart from the beginning.

Example, first some tasks:

.. code-block:: python

    from redengine.tasks import FuncTask

    @FuncTask(name="my-task-1")
    def myfunc():
        ...

    @FuncTask(name="my-task-2")
    def myfunc():
        ...

    @FuncTask(name="my-task-3")
    def myfunc():
        ...

Then we create a sequence with interval:

.. code-block:: python

    from redengine.extensions import Sequence
    Sequence(
        ["my-task-1", "my-task-2", "my-task-3"], 
        interval="time of day between 15:00 and 19:00"
    )

or a sequence without interval:

.. code-block:: python

    from redengine.extensions import Sequence
    Sequence(
        ["my-task-1", "my-task-2", "my-task-3"], 
    )
