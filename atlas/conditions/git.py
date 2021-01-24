
from atlas.core.conditions import Statement

try:
    from git import Repo
except ImportError:
    # Cannot use gitpython
    # TODO: raise warning
    pass


@Statement.from_func(historical=False, quantitative=False, use_globals=True)
def IsGitBehind(root=None, fetch=False, **kwargs):
    "Check whether the GIT repository is behind"
    repo = Repo(root)
    if fetch:
        repo.remotes.fetch()
    try:
        commits_behind = repo.iter_commits('master..origin/master')
        next(commits_behind)
    except StopIteration:
        return False
    else:
        return True