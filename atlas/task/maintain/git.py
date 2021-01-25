
from atlas.core.task import Task, register_task_cls
try:
    from git import Repo
except ImportError:
    # Cannot use gitpython
    # TODO: raise warning
    pass


@register_task_cls
class GitFetch(Task):
    # Tested (manually)
    def execute_action(self, root=None, **kwargs):
        # Requires gitpython
        repo = Repo(root)
        origin = repo.remotes.origin
        origin.fetch()

@register_task_cls
class GitPull(Task):
    # Tested (manually)
    def execute_action(self, root=None, branch="master", **kwargs):
        # Requires gitpython
        repo = Repo(root)
        origin = repo.remotes.origin
        origin.pull(branch)
