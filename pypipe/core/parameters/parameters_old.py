
from pypipe.utils import is_pickleable
from pypipe.utils.meta.func.func import parse_return
from pypipe.utils.meta.check.strong_type import is_instance
import multiprocessing as mp
from queue import Empty

from textwrap import dedent
from pypipe.utils.meta.code.format import declare_variable, to_expression

import pandas as pd

class Parameters:
    """Pool of parameters

    params = Parameters()
    args, kwargs = params[mytask]


    Parameters workflow (planned):
        Single process:
            Scheduler.__init__
                Set up the parameters
            Scheduler.run_task
                Send parameters to a task
            Task.__call__
                Materialize the parameters
            Scheduler.run_task
                Set return value to parameters

        Multi process:
            MultiScheduler.__init__
                Set up the parameters
            MultiScheduler.setup
                Set up the queue (communication) for return values of tasks

            MultiScheduler.run_task_as_process
                Remove unpicklable parameters
                and send them to the child process
            _run_task_as_process (child process)
                Pass parameters to the task 
                and pass the return value to the main 
                process through queue
            Task.__call__
                Materialize the parameters and pass them to the 
                function/notebook/script/command
            _run_task_as_process (child process)
                Pass the return value to the main 
                process through queue
            MultiScheduler.handle_logs
                Fetch the return values and set them to 
                global parameters for others to use
    """

    # TODO: How to pass scheduler to maintenance tasks? Done
    # TODO: How to pickle through multiprocessing?
    # TODO: Pass pickle/yaml etc. parameter sets to child processes without materializing first
    #   Now should be able to be implemented in parameters themselves

    def __init__(self, *parameters, scheduler=None):
        self.parameter_set = parameters
        self.parameter_ret = {} # Return values of tasks (that are used as inputs)

        # For maintenance tasks
        self.scheduler = scheduler

    def get_params(self, task):
        args = ()
        kwargs = {}
        for params in self.parameter_set:
            param_args, param_kwargs = params.extract()
            args = args + param_args
            kwargs.update(param_kwargs)

        for name, params in self.parameter_ret.items():
            if name in task.inputs:
                param_args, param_kwargs = params.extract()
                args = args + param_args
                kwargs.update(param_kwargs)

        if task.is_maintenance:
            kwargs["scheduler"] = self.scheduler
        return args, kwargs

    def filter_params(self, args, kwargs, task):
        n_pos_args = len(getattr(task, "pos_args", ()))
        kws = getattr(task, "kw_args", ())

        args = args[:n_pos_args]
        kwargs = {key:val for key, val in kwargs.items() if key in kws}
        return args, kwargs

    def __setitem__(self, task_name, return_values):
        "Set return values of a task"
        # TODO: Get parse_return from pybox
        args, kwargs = parse_return(return_values)
        #self.returns[task.name] = (args, kwargs)
        self.parameter_ret[task_name]  = StaticParameters(*args, **kwargs)

    def __getitem__(self, task):
        "Get parameters for a task"
        # TODO: return Parameters instead and let the task materialize
        args, kwargs = self.get_params(task)
        #dep_args, dep_kwargs = self.get_dependent_params(task)

        #args = args + dep_args
        #kwargs.update(dep_args)

        args, kwargs = self.filter_params(args, kwargs, task)
        params = ParameterSet(*args, **kwargs)

        # In case of multiprocessing
        if hasattr(self, "que"):
            params.que = self.que

        return params

    def listen(self):
        try:
            output = self.que.get(block=False)
        except Empty:
            pass
        else:
            name, args, kwargs = output
            self[name] = args, kwargs

    def materialize(self, include_scheduler=False):
        args = ()
        kwargs = {}
        for params in self.parameter_set:
            param_args, param_kwargs = params.extract()
            args = args + param_args
            kwargs.update(param_kwargs)

        for name, params in self.parameter_ret.items():
            param_args, param_kwargs = params.extract()
            args = args + param_args
            kwargs.update(param_kwargs)

        if include_scheduler:
            kwargs["scheduler"] = self.scheduler
        return args, kwargs

class ParameterSet:
    """A set of parameters (args & kwargs)
    
    A parameter set is a container of args and kwargs.
    Args and kwargs can be either:
        - Materialized (a typical Python object)
        - Unmaterialized (an instance of a subclass of Argument)
    
    Unmaterialized arguments are consumed by the task as it 
    sees to fit.

    Args (in this context) are positional arguments/data that
    are set to a task without giving a name. A tuple

    Kwargs (in this context) are keyword arguments that are 
    set to a task using a name/key. A dictionary
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def materialize(self):
        "Materialize the parameters to actual Python representation"
        args = tuple(
            arg.materialize() if isinstance(arg, Argument) else arg
            for arg in self.args
        )
        kwargs = {
            key: val.materialize() if isinstance(val, Argument) else val
            for key, val in self.kwargs.items()
        }
        return args, kwargs

    def extract(self):
        "Get args & kwargs as Python"
        return self.args, self.kwargs

    def extract_as_code(self):
        "Get args & kwargs as Python code"
        # Cannot turn args to code
        declarations = []
        imports = []
        for key, val in self.kwargs.items():
            # TODO: if instance, use pickle
            if is_instance(val):
                val = PickleArgument(val, f"{key}.pkl")

            if not isinstance(val, Argument):
                try:
                    declr, imp = declare_variable(var=key, value=val)
                except ValueError:
                    # Cannot turn to Python robustly --> use pickle
                    val = PickleArgument(val, f"{key}.pkl")
                    declr, imp = val.materialize_to_code(var=key)
            elif hasattr(val, "materialize_to_code"):
                declr, imp = val.materialize_to_code(var=key)
                # The argument defines it

            declarations.append(declr)
            if imp:
                imports.append(imp)
            
        imports = list(dict.fromkeys(imports)) # Removing duplicates
        if imports:
            imports += [""] # One empty line between imports and declarations
        return '\n'.join(imports + declarations)
        
    def remove_unpicklable(self):
        "Remove args and kwargs that cannot be pickled (in case of multiprocessing)"
        self.args = tuple(arg for arg in self.args if is_pickleable(arg))
        self.kwargs = {key: val for key, val in self.kwargs.items() if is_pickleable(val)}

    def _send(self, return_values, *, name):
        args, kwargs = parse_return(return_values)
        self.que.put((name, args, kwargs))

class StaticParameters(ParameterSet):

    def __init__(self, *static_args, **static_kwargs):
        self.args = static_args
        self.kwargs = static_kwargs

    def extract(self):
        args = (args  for arg in self.args)
        return self.args, self.kwargs


class PickleParameters(ParameterSet):
    "Get parameters from pickle file"
    def __init__(self, file):
        self.file = file

    def extract(self):
        pass

class YamlParameters(ParameterSet):
    """Get parameters from YAML file
    
    Examples:
        In config.yaml
            -
            - arg 1
            - arg 2
            - arg 3
            - 
            kw1: 1
            kw2: 2
        >>> (('arg 1', 'arg 2', 'arg 3'), {'kw1': 1, 'kw2': 2})

        In config.yaml
            - arg 1
            - arg 2
            - arg 3
        >>> (('arg 1', 'arg 2', 'arg 3'), {})

        In config.yaml
                kw1: 1
                kw2: 2
        >>> ((), {'kw1': 1, 'kw2': 2})
    """

    def __init__(self, file):
        self.file = file

    def materialize(self):
        with open(self.file, 'r') as file:
            cont = yaml.safe_load(file)
        args = () if isinstance(cont, dict) else tuple(cont) if isinstance(cont, (tuple, list)) else (cont,)
        kwargs = cont if isinstance(cont, dict) else {}
        return args, kwargs

# Arguments
class Argument:
    "Argument is one parameter for a task that may or may not be materialized"

class YamlArgument(Argument):
    """[summary]

    Args:
        Argument ([type]): [description]
    """

    utils = dedent("""
    def _read_yaml(path, items=None):
        items = [] if items is None else items
        with open(path, 'r') as file:
            cont = yaml.safe_load(file)
            for item in items:
                cont = cont[item]
        return cont"""[1:])

    def __init__(self, file, items=None):
        self.file = file
        self.items = [] if items is None else items

    def materialize(self):
        with open(path, 'r') as file:
            cont = yaml.safe_load(file)
        
        for item in self.items:
            if isinstance(item, Argument):
                item = item.materialize()
            cont = cont[item]

        return cont

    def materialize_to_code(self, var):
        "Transform the argument to code. May be messy but made for Jupyter Notebooks etc."

        utils = self.utils
        code = f"{var} = read_yaml({self.file})"

        return code[1:], "import yaml", utils

class PickleArgument(Argument):
    """[summary]

    Args:
        Argument ([type]): [description]
    """

    def __init__(self, obj, file):
        pd.to_pickle(obj, file)
        self.file = file

    def materialize(self):
        return pd.read_pickle(self.file)

    def materialize_to_code(self, var):
        "Transform the argument to code. May be messy but made for Jupyter Notebooks etc."

        code = f"{var} = pd.read_pickle({to_expression(self.file)[0]})"

        return code, "import pandas as pd"