
from powerbase.config import parse_dict

def test_init_maintain(tmpdir, session):
    with tmpdir.as_cwd() as old_dir:
        scheduler = parse_dict(
            {
                "tasks": {
                    "git-fetch": {"class": "GitFetch"},
                    "git-pull": {"class": "GitPull"},
                    "pip-install": {"class": "PipInstall"},
                    "restart": {"class": "Restart"}
                },
            }
        )
        tasks = session.tasks
        assert [
            "git-fetch",
            "git-pull",
            "pip-install",
            "restart"
        ] == [session.get_task(task).name for task in tasks]