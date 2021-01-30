
from atlas.config import parse_dict
from atlas import session
from atlas.core.task.base import get_all_tasks, get_task

def test_init_maintain(tmpdir):
    session.reset()
    with tmpdir.as_cwd() as old_dir:

        scheduler = parse_dict(
            {
                "tasks": {
                    "git-.fetch": {"class": "GitFetch"},
                    "git-pull": {"class": "GitPull"},
                    "pip-install": {"class": "PipInstall"},
                    "restart": {"class": "Restart"}
                },
            }
        )
        tasks = get_all_tasks()
        assert [
            "git-fetch",
            "git-pull",
            "pip-install",
            "restart"
        ] == [get_task(task).name for task in tasks]