
from redengine.tasks import FuncTask
from redengine import Session

def test_init_maintain(tmpdir, session):
    with tmpdir.as_cwd() as old_dir:
        sess = Session.from_dict(
            {
                "tasks": {
                    "restart": {"class": "Restart"}
                },
            }
        )
        tasks = sess.tasks
        assert [
            "restart"
        ] == [sess.get_task(task).name for task in tasks]

def test_without_class():
    sess = Session.from_dict(
        {
            "tasks": {
                "my-task-1": {"path": "something.py", "func": "main"},
            },
        }
    )
    assert [
        ("my-task-1", FuncTask),
    ] == [(task.name, type(task)) for task in sess.tasks.values()]