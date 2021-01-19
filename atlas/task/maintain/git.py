
from atlas.core.task import Task

import os
import subprocess

class GitFetch(Task):

    def execute_action(self, repo=None, **kwargs):
        origin = repo.remotes.origin
        origin.fetch()

class GitPull(Task):

    def execute_action(self, repo=None, branch="master", **kwargs):
        origin = repo.remotes.origin
        origin.pull(branch)
