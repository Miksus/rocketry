


from .base import Task

import inspect
import importlib

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
            script_path = self.action
            spec = importlib.util.spec_from_file_location("task", script_path)
            task_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(task_module)

            task_func = getattr(task_module, self.main_func)
            self._task_func = task_func
        return self._task_func


class CommandTask(Task):
    """Task that executes a commandline command
    """
    timeout = None

    def execute_action(self, *args, **kwargs):
        command = self.action
        if args:
            command = [command] + list(args) if isinstance(command, str) else command + list(args)

        pipe = subprocess.Popen(command,
                                shell=True,
                                #stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                )
        try:
            outs, errs = pipe.communicate(timeout=self.timeout)
        except TimeoutExpired:
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


class JupyterTask(Task):
    """Task that executes a Jupyter Notebook
    """

    parameter_tag = "parameter"

    def __init__(self, *args, on_preprocess=None, param_names=None, clear_outputs=True, **kwags):
        self.on_preprocess = on_preprocess
        self.param_names = [] if param_names is None else param_names
        super().__init__(*args, **kwargs)
        self.clear_outputs = clear_outputs

    def filter_params(self, params):
        # TODO: Figure out way to include custom parameters
        nb = self.notebook
        param_cell = nb.get_cells(tags=[self.parameter_tag])[0]
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
            # to prevent double call
            on_finally=self.on_finish,
            on_success=self.on_success,
            on_failure=self.on_failure,
            parameters=kwargs,
            clear_outputs=self.clear_outputs,
            parameter_tag=self.parameter_tag
        )

    def process_preprocess(self, nb, **kwargs):
        self.set_params(nb, **kwargs)
        if self.on_preprocess is not None:
            self.on_preprocess(nb, **kwargs)

    def set_params(self, nb, **kwargs):
        param_cells = nb.get_cells(tags=[self.parameter_tag])

        cell = CodeCell.from_variable_dict(kwargs)
        cell.insert(0, "# This is autogenerated parameter cell\n")

        param_cells[0].overwrite(cell)

        for cell in param_cells:
            raise NotImplementedError

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