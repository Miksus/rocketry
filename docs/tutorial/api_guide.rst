.. _api-guide:

Runtime API Guide
=================

You may want to have the possibility to communicate with 
the scheduling session when it is running. Most common 
cases include running tasks manually, disabling tasks 
temporarily or changing some parameters. In some cases 
you may also want to create, modify or delete tasks 
when the scheduler is running.

For such purposes Red Engine provide API tasks that 
are permanently running and waiting for an input. 
These tasks can only be parallelized via threads as 
modifying data between processes is problematic.

API via HTTP
------------

There is a premade :py:class:`redengine.tasks.api.FlaskAPI` task for runtime 
communication via HTTP. It uses `Flask <https://flask.palletsprojects.com/>`_, 
`Waitress <https://docs.pylonsproject.org/projects/waitress>`_,
and `Flask Restful <https://flask-restful.readthedocs.io/en/latest/>`_, 
and you should install those if you wish to use this task.

.. warning::

    Be careful if you expose the API to the internet 
    as by default anyone who can access the server 
    can run arbitrary code. You can control who may do requests
    and for which endpoints by subclassing :py:class:`redengine.tasks.api.FlaskAPI` and overriding
    the method ``authenticate`` for custom behaviour.

.. note::

    The task don't save the newly created tasks or modifications
    to disk thus these are not maintained when restarting the 
    session. In order to maintain these, you can subclass :py:class:`redengine.tasks.api.FlaskAPI`
    and override method ``store_request`` to store the changes and override 
    ``get_requests`` to reimplement these changes when the the API is initiated.

To initiate the task, simply call:

.. code-block:: python

    from redengine.tasks.api import FlaskAPI
    FlaskAPI()

And when you start the scheduler, you can do 
HTTP requests to the scheduler in runtime. By 
default the API is hosted in localhost on port
5000 but you can change these if needed.

Here is a table of the endpoints:

=============  ========================  ===========================================
Endpoint       Methods                   Description
=============  ========================  ===========================================
/tasks         GET                       List of the tasks in the session
/task/<name>   GET, POST, PATCH, DELETE  Get, create, modify or delete a task
/parameters    GET, PATCH                Get or modify the session parameters
/config        GET, PATCH                Get or modify the session configurations
/session       GET                       Get information about the session
/logs          GET                       Get log records
/dependencies  GET                       Get the dependencies of tasks
=============  ========================  ===========================================


For example, you can get the list of tasks by simply going to the page
`http://localhost:5000/tasks <http://localhost:5000/tasks>`_ or requesting 
the page with cURL:

.. code-block:: console

    curl http://localhost:5000/tasks

You can also pass data with ``POST`` or ``PATCH`` methods as JSON format, 
for example creating a task:

.. code-block:: console

    curl --request POST \
         --data '{"class": "CodeTask", "start_cond":"another value", "code": "print('\''Hello World'\'')"}' \
         http://localhost:5000/tasks/my-new-task

Many of the endpoints support querying via URL parameters. There are 
several query methods supported but here are a couple of examples:

- `http://localhost:5000/logs?timestamp$min=2021-01-01&timestamp$max=2021-12-31 <http://localhost:5000/logs?timestamp$min=2021-01-01&timestamp$max=2021-12-31>`_
- `http://localhost:5000/logs?action=fail&action=terminate <http://localhost:5000/logs?action=fail&action=terminate>`_
- `http://localhost:5000/tasks?name$regex=scraper.%2 <http://localhost:5000/tasks?name$regex=scraper.%2>`_

Note that some special characters may need to be passed in an encoded 
format, for example *+* (encoded as *%2*).
