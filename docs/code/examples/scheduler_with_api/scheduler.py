import asyncio
import logging

from redengine import RedEngine
from redengine.args import Task
import uvicorn

app = RedEngine()

@app.task("false", on_startup=True, execution="thread")
def serve_api():
    "This is a standalone FastAPI application"
    # To prevent circular import, we import the FastAPI app here
    from api import app as app_fast
    app_fast.app_red = app

    server = uvicorn.Server(config=uvicorn.Config(app_fast, workers=1, loop="asyncio"))
    async def run_server():
        await server.serve()

    app.session['do_things'].disabled = True

    # Create an event loop and serve the server
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_server())
    loop.close()

    

@app.task("every 10 seconds", execution="main")
def do_things(task=Task()):
    ...
    print(f"""{task.name}
    Disabled: {task.disabled}
    Force run: {task.disabled}
    """)

if __name__ == "__main__":
    # Setting a stream handler so we see what happens
    task_logger = logging.getLogger("redengine.task")
    task_logger.addHandler(logging.StreamHandler())

    # Run the scheduler (and the API)
    app.run()