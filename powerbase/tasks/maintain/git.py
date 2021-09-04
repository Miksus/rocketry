
from powerbase.core.task import Task
try:
    from git import Repo
except ImportError:
    # Cannot use gitpython
    # TODO: raise warning
    pass


class GitFetch(Task):
    # Tested (manually)
    def execute_action(self, root=None, **kwargs):
        # Requires gitpython
        repo = Repo(root)
        origin = repo.remotes.origin
        origin.fetch()


class GitPull(Task):

    def __init__(self, branch="master", **kwargs):
        self.branch = branch
        super().__init__(**kwargs)

    def execute_action(self, root=None, **kwargs):
        # Requires gitpython
        branch = self.branch

        repo = Repo(root)
        origin = repo.remotes.origin
        origin.pull(branch)
