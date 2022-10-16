
Integrate Django (or Django Rest Framework)
===========================================

This cookbook will use DRF (Django REST Framework) as an example, but the syntax is exaclty
the same for Django.

First, let's create a new command for setting up our jobs (we will call it `inittasks.py`):

.. code-block:: python

    # Create Rocketry app
    from rocketry import Rocketry
    app = Rocketry(config={"task_execution": "async"})


    # Create some tasks

    @app.task('every 5 seconds')
    async def do_things():
        ...

    class Command(BaseCommand):
    help = "Setup the periodic tasks runner"

    def handle(self, *args, **options):
        app.run()

You can also update your `wsgi` file, but this is not the recommended way, as it will not work
if you use Gunicorn or Uvicorn, or any other HTTP server.

Next, you can just run in your `entrypoint` script (or in your shell) the following command:

.. code-block:: bash

   ... # connect to the database, set PRODUCTION=1, etc...

    # if you deploy on Docker, it's probably better to run this in the background,
    # so you can run your HTTP server afterwards
    python manage.py inittasks &


And you're set ! It's really as simple as that!

Now, you might have the following error if you use Querysets, or try to use the ORM in your task:

.. code-block:: python

   Django: SynchronousOnlyOperation: You cannot call this from an async context - use a thread or sync_to_async

Some guides might recommend to set `DJANGO_ALLOW_ASYNC_UNSAFE` to True in your shell before running the tasks.
This is not the recommended way.

For our example, we will use the same file for simplicity, but you can move it to another file, of course.

.. code-block:: python

    # Create Rocketry app
    from rocketry import Rocketry
    app = Rocketry(config={"task_execution": "async"})


    # this is a synchronous operation that will work in an async context!
    def do_things_with_users(name):
        for user in User.objects.filter(name=name):
            print(f'I did something with {user} !')

    @app.task('every 5 seconds')
    async def do_things():
        await sync_to_async(do_things_with_users)(name='John Doe')
        ...

    class Command(BaseCommand):
    help = "Setup the periodic tasks runner"

    def handle(self, *args, **options):
        app.run()

You can even manually run the `do_things_with_users` function from a view now,
if that's something you would want. Let's add this view in our `views.py` file:

.. code-block:: python

    from api.commands import inittasks as tasklist

    class TaskView(APIView):
        def get(self, request):

            """
                This function is not ran by our scheduler, and runs in a synchronous context in our example
            """

            name = request.GET.get('name')
            if not name :
                return Response({
                    'error': 'missing a parameter (expected something like '
                             '?name=job_name )'
                    }, status=HTTP_400_BAD_REQUEST)

            try:

                task = getattr(tasklist, name)

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                loop.run_until_complete(task())

            except Exception as err:

                return Response({
                    'error': 'task failure',
                    'logs': f'Failed with: {str(err)}',
                    }, status=HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                'message': 'successfully ran the task',
                }, status=HTTP_200_OK)


Note that you will only need to use `sync_to_async` if you use the asynchronous ORM.
