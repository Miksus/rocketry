import logging

import pytest
import redbird
from redbird.logging import RepoHandler
from redbird.repos import CSVFileRepo, SQLRepo
from rocketry import Rocketry
from rocketry.log import MinimalRecord, MinimalRunRecord, TaskLogRecord, TaskRunRecord

def get_csv(model, tmpdir):
    file = tmpdir.join("logs.csv")
    return CSVFileRepo(filename=str(file), model=model)

def get_sql(model, tmpdir):
    pytest.importorskip("sqlalchemy")
    return SQLRepo(conn_string="sqlite://", table="mylogs", if_missing="create", model=model, id_field="created")

@pytest.mark.parametrize("get_repo", [get_csv, get_sql])
@pytest.mark.parametrize("model", [MinimalRecord, MinimalRunRecord, TaskLogRecord, TaskRunRecord])
def test_cache(session, tmpdir, model, get_repo):
    if get_repo == get_sql and model in (TaskRunRecord, TaskLogRecord) and redbird.version_tuple[:3] <= (0, 6, 0):
        pytest.skip(reason="Red Bird <= 0.6.0 does not support date-like in SQL table creation")
    repo = get_repo(model=model, tmpdir=tmpdir)
    task_logger = logging.getLogger(session.config.task_logger_basename)
    task_logger.handlers = [
        RepoHandler(repo=repo),
        #logging.StreamHandler(sys.stdout)
    ]

    task = session.create_task(func=lambda: None, name="task 1")
    task.log_running()
    task.log_success()

    task.set_cached()
    
    logs = repo.filter_by().all()
    logs = [{"action": r.action, "task_name": r.task_name} for r in logs]
    assert task.status == "success"
    assert logs == [
        {"action": "run", "task_name": "task 1"},
        {"action": "success", "task_name": "task 1"}
    ]