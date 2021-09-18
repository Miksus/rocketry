Logging
=======

Red Engine's logging uses ``logging`` from Python standard library.
The main purpose of logging in Red Engine is to maintain the information
which task has run, failed or succeeded and when. This information is needed
to determine the state of many of the conditions. 

Red Engine extends the ``logging`` library to allow also reading log records.
This is conducted by special handlers that write the log records to a more 
structural format such as CSV or as JSON to MongoDB. There is also a logging
adapter used for automatically passing the task name to the extras of the 
task logger and for acting as an interface for querying the handlers.

Task Adapter
------------

.. autoclass:: redengine.core.log.TaskAdapter
   :members:


Querying the task adapter
-------------------------

As stated, ``TaskAdapter`` interfaces the task logging and 
it can be used for querying log records of a specific task.
This can be done with the method ``.get_records(...)`` and 
this method allow several different ways for querying.

.. testsetup:: *

   from redengine.core import Task
   from redengine.log import MemoryHandler, AttributeFormatter
   import logging
   logger = logging.getLogger('redengine.task')
   handler = MemoryHandler()
   handler.records = [
       {"task_name": "mytask", "action": "run", "created": 1638748800}, 
       {"task_name": "mytask", "action": "success", "created": 1638749400},
       {"task_name": "mytask", "action": "run", "created": 1638750000}, 
       {"task_name": "mytask", "action": "fail", "created": 1638750600},
   ]
   logger.handlers = [handler]

>>> from redengine.core import Task
>>> task = Task(name="mytask")
>>> # The TaskAdapter is found as task.logger attribute
>>> task_adapter = task.logger

Querying all:

>>> from pprint import pprint
>>> pprint(list(task_adapter.get_records()))
[{'action': 'run',
  'created': 1638748800,
  'task_name': 'mytask',
  'timestamp': datetime.datetime(2021, 12, 6, 2, 0)},
 {'action': 'success',
  'created': 1638749400,
  'task_name': 'mytask',
  'timestamp': datetime.datetime(2021, 12, 6, 2, 10)},
 {'action': 'run',
  'created': 1638750000,
  'task_name': 'mytask',
  'timestamp': datetime.datetime(2021, 12, 6, 2, 20)},
 {'action': 'fail',
  'created': 1638750600,
  'task_name': 'mytask',
  'timestamp': datetime.datetime(2021, 12, 6, 2, 30)}]

Querying list of actions:

>>> from pprint import pprint
>>> pprint(list(task_adapter.get_records(action=['success', 'fail'])))
[{'action': 'success',
  'created': 1638749400,
  'task_name': 'mytask',
  'timestamp': datetime.datetime(2021, 12, 6, 2, 10)},
 {'action': 'fail',
  'created': 1638750600,
  'task_name': 'mytask',
  'timestamp': datetime.datetime(2021, 12, 6, 2, 30)}]

Querying specific range:

>>> from pprint import pprint
>>> import datetime
>>> pprint(list(task_adapter.get_records(timestamp=(datetime.datetime(2021, 12, 6, 2, 10), datetime.datetime(2021, 12, 6, 2, 25)))))
[{'action': 'success',
  'created': 1638749400,
  'task_name': 'mytask',
  'timestamp': datetime.datetime(2021, 12, 6, 2, 10)},
 {'action': 'run',
  'created': 1638750000,
  'task_name': 'mytask',
  'timestamp': datetime.datetime(2021, 12, 6, 2, 20)}]


Prebuilt handlers
-----------------

.. testsetup:: *

   import logging
   logger = logging.getLogger('redengine.doctest')
   logger.setLevel(logging.INFO)
   

.. autoclass:: redengine.log.MemoryHandler

.. autoclass:: redengine.log.CsvHandler

.. autoclass:: redengine.log.MongoHandler

