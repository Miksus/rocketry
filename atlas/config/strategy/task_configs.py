
from pathlib import Path
from pybox.io import read_yaml


TASK_CONFIG_STRATEGIES = {}


class _TaskConfigMeta(type):
    def __new__(mcs, name, bases, class_dict):

        cls = type.__new__(mcs, name, bases, class_dict)
        if name == "TaskConfigBase":
            return cls
        else:
            TASK_CONFIG_STRATEGIES[cls.__name__] = cls
        return cls

class TaskConfigBase(metaclass=_TaskConfigMeta):
        
    def parse_dict(self, d):
        return {
            "start_cond": d.get("start_cond", d.get("start_condition")),
            "end_cond": d.get("end_cond", d.get("end_condition", None)),
            "timeout": d.get("timeout", None),
            "priority": d.get("priority", 1),
        }

class FileConfig(TaskConfigBase):

    """Find arguments for Task from a config file

    Raises:
        FileNotFoundError: [description]

    Returns:
        Dict: Arguments for Task (ie. FuncTask, ScriptTask etc.)
    """
    yaml_file = "config.yaml"

    readers = {
        ".yaml": read_yaml,
    }

    def __init__(self, filename="config.yaml", if_missing="ignore"):
        self.filename = Path(filename)
        if self.filename.suffix not in self.readers:
            raise NotImplementedError(f"FileConfig not implemented for config files: {self.filename.suffix}")
        self.if_missing = if_missing

    def __call__(self, path, root=None):
        path = Path(path)

        dir_ = self.get_dir(path)
        conf_file = dir_ / self.filename
        if not conf_file.exists():
            if self.if_missing == "raise":
                raise FileNotFoundError(conf_file)
            elif self.if_missing == "ignore":
                return {}
        reader = self.readers[conf_file.suffix]

        return reader(conf_file)

    def get_name(self, path, root=None):
        root_len = len(root.parts) if root is not None else 0
        folders = path.parts[root_len:]
        return '.'.join(folders)

    def has_yaml(self, path):
        return (path / self.yaml_file).is_file()

    def get_yaml(self, path):
        path = path / self.yaml_file

        cont = read_yaml(path)
        return self.parse_dict(cont)

    def get_dir(self, path):
        return path.parent if path.is_file() else path


class ProjectConfig(TaskConfigBase):

    def __init__(self, log_groups=False, **kwargs):
        self.log_groups = log_groups
        super().__init__(**kwargs)

    def get_name(self, path, root=None):
        dir_ = self.get_dir(path)
        root_len = len(root.parts)
        folders = dir_.parts[root_len:]
        return '.'.join(folders)

