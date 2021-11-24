.. _short-guide:

Short Guide
===========

This section is a quick walk through of the essentials
and the things you need to get started.

Here is a check list of things you need:

- Create a session
- Create tasks
- Start the session


Create a Session
----------------

First thing you need is a session. Session is an object that
stores all the tasks and (session level) parameters for the 
tasks. If you want you can configure a session yourself:

.. code-block:: python

    from redengine import Session

    # Create a session that logs in csv file
    Session(scheme="log_csv")

    ... # import or put your tasks here

    # Starting the scheduler
    session.start()

Create Tasks
------------

Tasks are the actual things you want to schedule. These can 
be simply Python functions but can be much more else also.
Next we will create some function tasks:

.. code-block:: python

    from redengine.tasks import FuncTask
    
    @FuncTask(start_cond="daily after 08:00")
    def wake_up():
        print("Waking up...")
        ... # Code to run once a day after 8 AM 

    @FuncTask(start_cond="every 2 hours")
    def check_messages():
        print("Checking messages...")
        ... # Code to run every 2 hours

    @FuncTask(start_cond="daily between 23:00 and 05:00")
    def go_to_bed():
        print("Going to bed...")
        ... # Code to run once a day between 11 PM and 5 AM

Remember to put/import this before starting your session.

We created three tasks: ``wake_up``, ``check_messages`` and ``go_to_bed``. 
The function ``wake_up`` runs once a day when it's after 8 AM, ``check_messages``
runs once in every 2 hours and ``go_to_bed`` runs once a day between 11 PM and 5 AM.
As you probably noted, the argument ``start_cond`` specifies when a task may start and 
there are a lot of built-in scheduling options and you can combine them using simple and, 
or and not operations. See more condition options :ref:`condition-syntax` and read more 
about conditions from :ref:`conditions-intro`. 

See more in :ref:`tasks`.

Start the session
-----------------

When you have set up the tasks, you can just start the session by:

.. code-block:: python

    session.start()


Putting together
----------------

Our program should now look something like this:

.. code-block:: python

    from redengine import Session
    from redengine.tasks import FuncTask

    # Create a session that logs in csv file
    Session(scheme="log_csv")

    # Tasks    
    @FuncTask(start_cond="daily after 08:00")
    def wake_up():
        print("Waking up...")
        ... # Code to run once a day after 8 AM 

    @FuncTask(start_cond="every 2 hours")
    def check_messages():
        print("Checking messages...")
        ... # Code to run every 2 hours

    @FuncTask(start_cond="daily between 23:00 and 05:00")
    def go_to_bed():
        print("Going to bed...")
        ... # Code to run once a day between 11 PM and 5 AM

    if __name__ == "__main__":
        # Starting the scheduler
        session.start()

