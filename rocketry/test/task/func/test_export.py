from rocketry.tasks import FuncTask

def test_to_dict(session):
    task1 = FuncTask(func=lambda: None, name="task 1", start_cond="every 10 seconds", session=session)
    task2 = FuncTask(func=lambda: None, name="task 2", start_cond="after task 'task 1'", session=session)

    task1.model_dump()
    task2.model_dump()

    task1.model_dump_json()
    task2.model_dump_json()
    pass
