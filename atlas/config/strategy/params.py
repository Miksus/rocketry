
from git import Repo
from pathlib import Path
from atlas.core.parameters import Parameters
from pybox.io import read_yaml

PARAM_STRATEGIES = {}

class ParamStrategyMeta(type):
    def __new__(mcs, name, bases, class_dict):

        cls = type.__new__(mcs, name, bases, class_dict)
        PARAM_STRATEGIES[cls.__name__] = cls
        return cls


class RepoParams(metaclass=ParamStrategyMeta):

    def __init__(self, path):
        self.path = path

    def __call__(self, root):
        root = Path(root)
        return Parameters(repo=Repo(root))

class ParamFolder(metaclass=ParamStrategyMeta):
    def __init__(self, path=None):
        self.path = path

    def __call__(self, root, **kwargs):
        root = Path(self.path) if self.root is not None else Path(root)
        d = {}
        for file in root.glob("*.yaml"):
            d.update(read_yaml(file))
        return Parameters(**d)


class ParamFile(metaclass=ParamStrategyMeta):

    def __init__(self, files, root=None):
        self.files = files
        self.root = root

    def __call__(self, root):
        root = Path(self.root) if self.root is not None else Path(root)
        return Parameters(read_yaml(root / "config/public.yaml"))