
.. _handbook-cond-pipeline:

Task Pipelines
==============

There are also conditions related to if another task has 
runned/succeeded/failed before the task we are setting the
starting condition. These are useful for creating task 
depenencies or task pipelines. 

.. literalinclude:: /code/conds/api/pipe_single.py
    :language: py

You can also pipe multiple at the same time to avoid long
logical statements:

.. literalinclude:: /code/conds/api/pipe_multiple.py
    :language: py