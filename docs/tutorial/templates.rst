
Templates
=========

There are various other premade project templates than just the 
minimal we discussed to help you get started. Choose a template
that suits the complexity of your project.

To create a project from given template (in this case `simple`):

.. code-block:: console

   python -m redengine create myproject --template simple

Premade Templates
-----------------

- ``standalone``: The most simplistic example. Only one file system.
- ``minimal``: A simplistic system for quick start and small projects.
- ``simple``: Has most of the features offered by Red Engine but not more.
  Useful to get familiar with the framework or for moderate sized projects.
- ``package``: Similar as `simple` but a Python package.
- ``complex``: Full featured production grade template. Also has:

  - Environments: tasks not belonging to the run environment are disabled
    and parameters can be environment specific.
  - Command line interface: The scheduler is started from command line and 
    individual tasks can be run manually.