
import os
from redengine.core.task import Task
from pathlib import Path

class _GitTask(Task):
    git_dir = ".git"

    def get_repo_root(self, path=None):
        if path is None:
            path = os.getcwd()
        for path in Path(path).parents:
            # Check whether "path/.git" exists and is a directory
            git_dir = path / self.git_dir
            if git_dir.is_dir():
                return path
        else:
            raise FileNotFoundError(f"Repo root not found for {path!r}")
        

class GitFetch(_GitTask):
    # Tested (manually)
    def execute_action(self, git_repo=None, **kwargs):
        # Requires gitpython
        from git import Repo
        path = self.get_repo_root(git_repo)
        repo = Repo(path)
        origin = repo.remotes.origin
        origin.fetch()


class GitPull(_GitTask):

    def __init__(self, branch="master", **kwargs):
        self.branch = branch
        super().__init__(**kwargs)

    def execute_action(self, git_repo=None, **kwargs):
        # Requires gitpython
        from git import Repo
        path = self.get_repo_root(git_repo)

        branch = self.branch

        repo = Repo(path)
        origin = repo.remotes.origin
        origin.pull(branch)
