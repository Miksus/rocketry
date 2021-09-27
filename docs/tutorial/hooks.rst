.. _hooks:

Extending with hooks
====================

Hooks are simply functions or generators that are 
executed in specific parts of Red Engine's code. 
These are useful for building your logic for 
specific situations where subclassing a base class
would be too complicated.

Hook also can be a generator in which case the code 
before the first ``yield`` is executed before the 
hook's section and the code after it will be executed
after the hook's section. 


.. testsetup:: func_hook

   cleanup()

.. testsetup:: gen_hook

   cleanup()

.. autofunction:: redengine.core.Task.hook_init
   :noindex:

.. testcleanup:: func_hook

   cleanup()

.. testcleanup:: gen_hook

   cleanup()

.. autofunction:: redengine.core.Scheduler.hook_startup
   :noindex:

.. autofunction:: redengine.core.Scheduler.hook_cycle
   :noindex:

.. autofunction:: redengine.core.Scheduler.hook_shutdown
   :noindex:
