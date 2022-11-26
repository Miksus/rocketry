import asyncio
from rocketry import Rocketry

app = Rocketry(execution="async")

@app.task()
async def do_things():
    ...

async def main():
    "Launch Rocketry app (and possibly something else)"
    rocketry_task = asyncio.create_task(app.serve())
    # Start possibly other async apps
    await rocketry_task

if __name__ == "__main__":
    asyncio.run(main())
