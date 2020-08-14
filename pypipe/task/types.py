


from .base import Task
from .config import parse_config

from pathlib import Path
import inspect
import importlib

from jubox import JupyterNotebook, CodeCell
from jubox.builtin import run_notebook

class FuncTask(Task):
    """Function Task, task that executes a function
    """
    def execute_action(self, *args, **kwargs):
        "Run the actual, given, task"
        return self.action(*args, **kwargs)

    def get_default_name(self):
        func = self.action
        return func.__name__
        
    def filter_params(self, params):
        return self.get_reguired_params(self.action, params)

    @staticmethod
    def get_reguired_params(func, params):
        sig = inspect.signature(func)
        required_params = [
            val
            for name, val in sig.parameters
            if val.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD, # Normal argument
                inspect.Parameter.KEYWORD_ONLY # Keyword argument
            )
        ]
        kwargs = {}
        for param in required_params:
            if param in params:
                kwargs[param] = params[param]
        return kwargs

class ScriptTask(Task):
    """Task that executes a Python script

    ScriptTask("folder/subfolder/main.py")
    ScriptTask("folder/subfolder/mytask.py")
    """
    main_func = "main"

    def execute_action(self, *args, **kwargs):
        task_func = self.get_task_func()
        return task_func()

    def get_default_name(self):
        file = self.action
        return '.'.join(file.parts).replace(r'/main.py', '')

    def filter_params(self, params):
        task_func = self.get_task_func()
        return FuncTask.get_reguired_params(task_func, params)

    def process_finish(self, *args, **kwargs):
        del self._task_func
        super().process_finish(*args, **kwargs)


    def get_task_func(self):
        if not hasattr(self, "_task_func"):
            # _task_func is cached to faster performance
            task_module = self.get_module(self.action)
            task_func = getattr(task_module, self.main_func)
            self._task_func = task_func
        return self._task_func

    @classmethod
    def from_file(cls, path, **kwargs):
        confs = cls._get_config(cls.get_module(path))
        confs.update(kwargs)
        obj = cls(action=path, **confs)
        return obj

    @classmethod
    def from_project_folder(cls, path, main_file="main.py"):
        """get all tasks from a project folder
        Project folder is a folder with sub folders 
        that contain 'main files' used as
        the actual tasks. 

        Example:
            path structure:
                | my_tasks/
                |____ fetch/
                     |____ prices/
                     |    |____ main.py
                     |____ index/
                          |____ main.py
                          |____ utils.py
                          |____ tickers/
                               |____ main.py
                               |____ utils.py

            ScriptTask.from_project_folder("my_tasks")
            >>> [Task(name=("fetch", "prices"), ...), 
                Task(name=("fetch", "index"), ...), 
                Task(name=("fetch", "index", "tickers"), ...)]
            ....
        """
        root = Path(path)

        tasks = []
        glob = f"**/{main_file}"
        for file in root.glob(glob):
            root_len = len(root.parts)
            name = file.parts[root_len:-1]
            tasks.append(cls.from_file(file, name=name)) 
        return tasks

    @classmethod
    def from_module_folder(cls, path, glob="*.py"):
        """get all tasks from folder
        
        Example:
            path structure:
                | my_tasks/
                |____ fetch_prices.py
                |____ fetch_index.py

            ScriptTask.from_module_folder("my_tasks")
            >>> [Task(name="fetch_prices", ...), Task(name="fetch_index", ...)]
        """
        root = Path(path)

        tasks = []
        for file in root.glob(glob):
            tasks.append(cls.from_file(file, name=file.name.replace(file.suffix, ""))) 
        return tasks

    @staticmethod
    def get_module(path):
        spec = importlib.util.spec_from_file_location("task", path)
        task_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(task_module)
        return task_module

    @staticmethod
    def _get_config(module):
        "Get config from the module"

        confitems = {
            "start_cond": "START_CONDITION",
            "run_cond": "RUN_CONDITION",
            "end_cond": "END_CONDITION",
            "dependent": "DEPENDENT",
            "execution": "EXECUTION",
        }
        confs = {}
        for key, var in confitems.items():
            if hasattr(module, var):
                confs[key] = getattr(module, var)
        return confs


class CommandTask(Task):
    """Task that executes a commandline command
    """
    timeout = None

    def __init__(self, *args, cwd=None, shell=False, **kwags):
        super().__init__(*args, **kwargs)
        self.kwargs_popen = {"cwd": cwd, "shell":shell}
        # About shell: https://stackoverflow.com/a/36299483/13696660

    def execute_action(self, *args, **kwargs):
        command = self.action
        if args:
            command = [command] + list(args) if isinstance(command, str) else command + list(args)
        # command can be: "myfile.bat", "echo Hello!", ["python", "v"]
        # https://stackoverflow.com/a/5469427/13696660
        pipe = subprocess.Popen(command,
                                #shell=True,
                                capture_output=True,
                                #stdin=subprocess.PIPE,
                                #stdout=subprocess.PIPE,
                                #stderr=subprocess.PIPE,
                                **self.kwargs_popen
                                )
        try:
            outs, errs = pipe.communicate(timeout=self.timeout)
        except subprocess.TimeoutExpired:
            # https://docs.python.org/3.3/library/subprocess.html#subprocess.Popen.communicate
            pipe.kill()
            outs, errs = pipe.communicate()
            raise
        
        if pipe.returncode != 0:
            errs = errs.decode("utf-8", errors="ignore")
            raise OSError(f"Failed running command: \n{errs}")
        return stout

    def filter_params(self, params):
        # TODO: Figure out way to include custom parameters
        return {}

    def get_default_name(self):
        command = self.action
        return command if isinstance(command, str) else ' '.join(command)

    @classmethod
    def from_folder(cls, path):
        "get all tasks from folder"
        root = Path(path)

        types = ("**/*.bat", "**/*.sh")

        tasks = []
        for type_ in types:
            for file in root.glob(type_):
                tasks.append(cls.from_file(file)) 
        return tasks

class JupyterTask(Task):
    """Task that executes a Jupyter Notebook
    """

    parameter_tag = "parameter"

    def __init__(self, *args, on_preprocess=None, param_names=None, clear_outputs=True, **kwargs):
        self.on_preprocess = on_preprocess
        self.param_names = [] if param_names is None else param_names
        super().__init__(*args, **kwargs)
        self.clear_outputs = clear_outputs

    def filter_params(self, params):
        # TODO: Figure out way to include custom parameters
        nb = self.notebook
        try:
            param_cell = nb.cells.get(tags=[self.parameter_tag])[0]
        except IndexError:
            return {}
        code = param_cell.source
        param_vars = re.findall(r"""
        (?<=\n)                               # Must start with new line
        (?P<var_name>[A-Za-z_][A-Za-z_0-9]*)  # Variable name must start with letter, underscore but then numbers are allowed
        [ ]*=[ ]*                             # Can have spaces before and after the equal sign
        """, '\n' + code, re.VERBOSE)

        return {key:val for key, val in params.items() if key in param_vars or key in self.param_names}

    def execute_action(self, **kwargs):
        nb = self.notebook
        self.process_preprocess(nb, **kwargs)


        nb = run_notebook(
            notebook=nb,
            # Note, we do not pass the methods 
            # (process_finish, process_success etc.)
            # to prevent double call
            on_finally=self.on_finish,
            on_success=self.on_success,
            on_failure=self.on_failure,
            # parameters=kwargs, # Parameters are set elsewhere
            clear_outputs=self.clear_outputs,
            parameter_tag=self.parameter_tag
        )

    def process_preprocess(self, nb, **kwargs):
        self.set_params(nb, **kwargs)
        if self.on_preprocess is not None:
            self.on_preprocess(nb, **kwargs)

    def set_params(self, nb, **kwargs):
        # TODO:
        #   An option to set arbitrary parameters using picke
        #       1. write the parameter(s) to a pickle file
        #       2. manipulate param cell in a way that it reads
        #          these parameters
        #       3. Run the notebook
        #       4. Possibly clear the pickle files
        try:
            param_cell = nb.cells.get(tags=[self.parameter_tag])[0]
        except IndexError:
            return

        cell = CodeCell.from_variable_dict(kwargs)
        cell.insert(0, "# This is autogenerated parameter cell\n")

        param_cell.overwrite(cell)

    def process_failure(self, exception):
        # on_failure is called already
        pass
    
    def process_success(self, output):
        # on_success is called already
        pass

    def process_finish(self, status):
        # on_finish is called already
        # Deleting the notebook so next time the file is refetched
        del self.notebook

    def get_default_name(self):
        return self.action

    @property
    def notebook(self):
        if not hasattr(self, "_notebook"):
            self._notebook = JupyterNotebook(self.action)
        return self._notebook

    @notebook.deleter
    def notebook(self):
        del self._notebook

    @classmethod
    def from_file(cls, path):

        obj = cls(action=path, **parse_config(path))
        return obj
        
    @classmethod
    def from_folder(cls, path, glob=None, name_func=None, **kwargs):
        """get all tasks from folder
        
        Example:
            path structure:
                | my_notebooks/
                |____ do_report.ipynb
                |____ do_analysis.ipynb
                
            JupyterTask.from_folder("my_notebooks")
            >>> [Task(name="do_report", ...), Task(name="do_analysis", ...)]
        """
        root = Path(path)

        glob = "*.ipynb" or glob
        name_func = (
            (lambda relative_path: tuple(part.replace('.ipynb', '') for part in relative_path.parts)) 
            if name_func is None else name_func
        )

        tasks = []
        for file in root.glob(glob):

            kwargs.update(cls._get_conf_from_file(file))
            task_name = name_func(Path(*file.parts[len(root.parts):]))
            tasks.append(cls(action=path, name=task_name, **kwargs))
        return tasks

    @staticmethod
    def _get_conf_from_file(path):
        nb = JupyterNotebook(path)
        cond_cell = nb.cells.get(tags=["conditions"])[0]
        src = cond_cell.source

        conds = {
        }
        exec(src, conds)
        start_condition = conds.pop("start_condition", None)
        end_condition = conds.pop("end_condition", None)
        run_condition = conds.pop("run_condition", None)
        dependent = conds.pop("dependent", None)
        execution = conds.pop("execution", None)

        return {
            "start_cond": start_condition,
            "end_cond": end_condition,
            "run_cond": run_condition,
            "dependent": dependent,
            "execution": execution,
        }


    def _get_config(self, path):
        notebook = JupyterNotebook(path)
        conf_cell = notebook.cells.get(tags=["taskconf"])
        conf_string = conf_cell.source
        conf_string