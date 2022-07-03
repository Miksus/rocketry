from threading import Thread
from typing import List
from fastapi import FastAPI
from scheduler import app as app_red
from redengine.log import LogRecord

app = FastAPI()

@app.get("/logs")
async def get_logs() -> List[LogRecord]:
    "Get logs"
    log_repo = app_red.session.get_repo()
    return log_repo.filter_by().all()

@app.get("/tasks")
async def get_task():
    "Get all tasks"
    return list(app_red.session.tasks)

@app.patch("/tasks/{task_name}")
async def update_task(task_name, values:dict):
    task = app_red.session[task_name]
    for key, val in values.items():
        setattr(task, key, val)

@app.on_event("startup")
async def startup_event():
    thread = Thread(target = app_red.run)
    thread.start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1)