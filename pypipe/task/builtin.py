


from .base import Task


class FuncTask(Task):
    """Function Task, task that executes a function
    """
    def execute_action(self, *args, **kwargs):
        "Run the actual, given, task"
        return self.action(*args, **kwargs)

    def get_default_name(self):
        func = self.action
        return func.__name__


class ScriptTask(Task):
    """Task that executes a Python script
    """
    main_func = "main"

    def execute_action(self, *args, **kwargs):

        script_path = self.action
        spec = importlib.util.spec_from_file_location("task", script_path)
        task_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(task_module)

        task_func = getattr(task_module, self.main_func)
        return task_func()

    def get_default_name(self):
        file = self.action
        return '.'.join(file.parts).replace(r'/main.py', '')


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

    def get_default_name(self):
        command = self.action
        return command if isinstance(command, str) else ' '.join(command)


class JupyterTask(Task):
    """Task that executes a Jupyter Notebook
    """
    def execute_action(self):
        nb = JupyterNotebook(self.action)

        if self.on_preprocess is not None:
            self.on_preprocess(nb)

        self._notebook = nb
        nb(inplace=True)

    def process_failure(self, exception):
        if self.on_failure:
            self.on_failure(self._notebook, exception=exception)
    
    def process_success(self, output):
        if self.on_success:
            self.on_success(self._notebook)

    def process_finish(self, status):
        if self.on_finish:
            self.on_finish(self._notebook, status)
        del self._notebook

    def get_default_name(self):
        return self.action