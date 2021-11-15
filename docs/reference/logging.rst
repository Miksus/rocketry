
Logging Adapter
===============

.. autoclass:: redengine.core.log.TaskAdapter
   :members:


Logging Handlers
================

.. testsetup:: *

   import logging
   logger = logging.getLogger('redengine.doctest')
   logger.setLevel(logging.INFO)
   

MemoryHandler
-------------

.. autoclass:: redengine.log.MemoryHandler

CsvHandler
----------

.. autoclass:: redengine.log.CsvHandler

MongoHandler
------------

.. autoclass:: redengine.log.MongoHandler

