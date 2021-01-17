
from atlas.core.conditions import Statement

try:
    from git import Repo
except ImportError:
    # Cannot use gitpython
    # TODO: raise warning
    pass

def fetch(repo):
    for remote in repo.remotes:
        remote.fetch()

def get_commits_behind(repo):
    # TODO: Put to Pybox
    fetch(repo)
    return repo.iter_commits('master..origin/master')


@Statement.from_func(historical=False, quantitative=False)
def IsGitBehind(repo, **kwargs):
    "Check whether the GIT repository is behind"

    try:
        next(get_commits_behind(repo))
    except StopIteration:
        return False
    else:
        return True