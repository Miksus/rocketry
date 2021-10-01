
from redengine.tasks import PyScript
from redengine import Session

def test_init_maintain(tmpdir, session):
    with tmpdir.as_cwd() as old_dir:
        sess = Session.from_dict(
            {
                "tasks": {
                    "git-fetch": {"class": "GitFetch"},
                    "git-pull": {"class": "GitPull"},
                    "pip-install": {"class": "PipInstall"},
                     "restart": {"class": "Restart"}
                },
            }
        )
        tasks = sess.tasks
        assert [
            "git-fetch",
            "git-pull",
            "pip-install",
             "restart"
        ] == [sess.get_task(task).name for task in tasks]

def test_without_class():
    sess = Session.from_dict(
        {
            "tasks": {
                "my-task-1": {"path": "something.py"},
            },
        }
    )
    assert [
        ("my-task-1", PyScript),
    ] == [(task.name, type(task)) for task in sess.tasks.values()]