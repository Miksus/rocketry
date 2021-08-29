
from powerbase.config import parse_dict

def test_init_maintain(tmpdir, session):
    with tmpdir.as_cwd() as old_dir:
        sess = parse_dict(
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