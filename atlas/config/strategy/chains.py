
from atlas.task.maintain import GitFetch, GitPull, PipInstall, Restart
from atlas.conditions import TasksAlive, IsGitBehind, DependSuccess

from .tasks import TaskFinderBase

# Premade chains
class AutoUpdate(TaskFinderBase):
    def __init__(self, start_cond, **kwargs):
        self.start_cond = start_cond

    def __call__(self, **kwargs):
        start_cond = self.start_cond

        git_fetch = GitFetch(
            start_cond=start_cond,
            name="git_fetch"
        )
        git_pull = GitPull(
            # Note: git pull succeedes even or not there are new changes
            # To have pip install run after changes has been pulled, we
            # split git fetch and git pull and checking master vs origin/master
            # allows this task to make sure it's run only when new changes
            # so that other tasks can hook on this one.
            start_cond=IsGitBehind(fetch=False),
            name="git_pull"
        )
        pip_install = PipInstall(
            start_cond=DependSuccess(depend_task=git_pull),
            parameters={"file": "requirements.txt"},
            name="pip_install"
        )
        restart = Restart(
            start_cond=DependSuccess(depend_task=pip_install),
            name="restart"
        )
        return [git_fetch, git_pull, pip_install, restart]

