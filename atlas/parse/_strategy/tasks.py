
from atlas.task import PyScript

from .task_configs import FileConfig
from pathlib import Path



from atlas.conditions import IsGitBehind, DependSuccess

# This dictionary is used by parse strategy to
# get the correct finder class from string 
# (name of the finder class)
CLS_STRATEGIES = {} 

class _TaskStrategyMeta(type):
    def __new__(mcs, name, bases, class_dict):
        cls = type.__new__(mcs, name, bases, class_dict)

        if name == "TaskFinderBase":
            # Don't register base class
            return cls
        CLS_STRATEGIES[cls.__name__] = cls
        return cls

class TaskFinderBase(metaclass=_TaskStrategyMeta):

    default_configs = None

    def __init__(self, config=None):
        self.config = config

    def get_config(self, **kwargs) -> dict:
        "Get arguments for a Task"
        if not self.config:
            if self.default_configs is None:
                return {}
            return self.default_configs(**kwargs)
        if isinstance(self.config, dict):
            # Start condition etc. were defined 
            # in the config section of the task
            # finders in actual configs
            return self.config.copy()
        else:
            # Configs is a ConfigFinder
            return self.config(**kwargs)

class ProjectFinder(TaskFinderBase):

    """Find tasks from nested folders

    Example:
    --------
        Folders:
        ___my_tasks/
           |_________task_1/
           |         |______main.py
           |         |______config.yaml
           |
           |_________task_2/
                     |______sub_task_1/
                            |___________main.py
                            |___________config.yaml

        ProjectFinder(
            path="path/to/my_tasks",
            config=FileConfig(path="config.yaml")
        )()
        >>> [
            PyScript(name="task_1", path="my_tasks/task_1/main.py", **config),
            PyScript(name="task_2.sub_task_1", path="my_tasks/task_2/sub_task_1/main.py", **config),
        ]


    Returns: 
        List[Task] : Tasks (maintainer or normal) for a scheduler
    """
    default_configs = FileConfig("config.yaml")

    def __init__(self, path, main_func=None, **kwargs):
        self.path = Path(path)
        self.main_func = main_func
        super().__init__(**kwargs)

    def __call__(self, root=None, **kwargs):
        root = self.path
        tasks = []

        for script_path in self.path.glob("**/main.py"):

            
            config = self.get_config(path=script_path.parent)
            if "name" not in config:
                # Default name is the directories between self.path <--> main.py
                config["name"] = '.'.join(script_path.parts[len(root.parts):-1])

            tasks.append(
                PyScript(script_path, main_func=self.main_func, **config)
            )

        return tasks


class NotebookStrategy(TaskFinderBase):
    def __init__(self, path, main_func=None, config=None, root=None):
        self.path = path
        self.config = config
        self.main_func = main_func

        # Used to determine where project folder start
        self.root = root

    def __call__(self, **kwargs):
        root = self.path

        tasks = []

        for nb_path in root.glob("**/*.ipynb"):

            #name = '.'.join(script_path.parts[len(root.parts):-1])
            config = self.config_finder(nb_path)

            tasks.append(
                JupyterTask(nb_path, **config)
            )

        return tasks
