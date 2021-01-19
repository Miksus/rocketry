
from atlas.core.task import Task

class GitFetch(Task):

    def execute_action(self, repo=None, **kwargs):
        # Requires gitpython
        origin = repo.remotes.origin
        origin.fetch()

class GitPull(Task):

    def execute_action(self, repo=None, branch="master", **kwargs):
        # Requires gitpython
        origin = repo.remotes.origin
        origin.pull(branch)
