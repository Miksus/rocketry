
from atlas.core.task import Task
try:
    from git import Repo
except ImportError:
    # Cannot use gitpython
    # TODO: raise warning
    pass


class GitFetch(Task):
    # Tested (manually)
    def execute_action(self, repo=None, **kwargs):
        # Requires gitpython
        repo = Repo(repo)
        origin = repo.remotes.origin
        origin.fetch()

class GitPull(Task):
    # Tested (manually)
    def execute_action(self, repo=None, branch="master", **kwargs):
        # Requires gitpython
        repo = Repo(repo)
        origin = repo.remotes.origin
        origin.pull(branch)
