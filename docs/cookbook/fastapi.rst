
Integrate FastAPI
=================

The simplest way to combine FastAPI app with Rocketry app 
is to start both as async tasks. You can modify the Rocketry's
runtime session in FastAPI. There is an existing example project:
`Rocketry with FastAPI (and React) <https://github.com/Miksus/rocketry-with-fastapi>`_

First, we create a simple Rocketry app
(let's call this ``scheduler.py``):

.. code-block:: python

    # Create Rocketry app
    from rocketry import Rocketry
    app = Rocketry(execution="async")


    # Create some tasks

    @app.task('every 5 seconds')
    async def do_things():
        ...

    if __name__ == "__main__":
        app.run()

Then we create a FastAPI app and manipulate the Rocketry
app in it (let's call this ``api.py``):

.. code-block:: python

    # Create FastAPI app
    from fastapi import FastAPI
    app = FastAPI()

    # Import the Rocketry app
    from scheduler import app as app_rocketry
    session = app_rocketry.session

    @app.get("/my-route")
    async def get_tasks():
        return session.tasks

    @app.post("/my-route")
    async def manipulate_session():
        for task in session.tasks:
            ...

    if __name__ == "__main__":
        app.run()

Then we combine these in one module
(let's call this ``main.py``):

.. code-block:: python

    import asyncio
    import uvicorn

    from api import app as app_fastapi
    from scheduler import app as app_rocketry


    class Server(uvicorn.Server):
        """Customized uvicorn.Server
        
        Uvicorn server overrides signals and we need to include
        Rocketry to the signals."""
        def handle_exit(self, sig: int, frame) -> None:
            app_rocketry.session.shut_down()
            return super().handle_exit(sig, frame)


    async def main():
        "Run scheduler and the API"
        server = Server(config=uvicorn.Config(app_fastapi, workers=1, loop="asyncio"))

        api = asyncio.create_task(server.serve())
        sched = asyncio.create_task(app_rocketry.serve())

        await asyncio.wait([sched, api])

    if __name__ == "__main__":
        asyncio.run(main())

Note that we need to subclass the ``uvicorn.Server`` in order 
to make sure the scheduler is also closed when the FastAPI app
closes. Otherwise the system might not respond on keyboard interrupt.