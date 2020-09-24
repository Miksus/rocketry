

class Parameters:
    """Pool of parameters

    params = Parameters()
    args, kwargs = params[mytask]
    """

    # TODO: How to pass scheduler to maintenance tasks?
    # TODO: How to pickle through multiprocessing?

    def __init__(self, *parameters):
        self.parameter_set = parameters
        self.parameter_ret = {} # Return values of tasks (that are used as inputs)

    def get_params(self, task):
        args = ()
        kwargs = {}
        for params in self.parameter_set:
            args = args + params.args
            kwargs.update(params.kwargs)

        for name, params in self.parameter_ret.items():
            if name == task.name:
                args = args + params.args
                kwargs.update(params.kwargs)
        return args, kwargs

    def filter_params(self, args, kwargs, task):
        n_pos_args = task.n_pos_args
        kws = task.kw_args

        args = args[:n_pos_args]
        kwargs = {key:val for key, val in kwargs.items() if key in kws}
        return args, kwargs

    def __setitem__(self, task, return_values):
        "Set return values of a task"
        args, kwargs = parse_return(return_values)
        #self.returns[task.name] = (args, kwargs)
        self.parameter_ret[task]  = StaticParameters(*args, **kwargs)

    def __getitem__(self, task):
        "Get parameters for a task"
        args, kwargs = self.get_params(task)
        #dep_args, dep_kwargs = self.get_dependent_params(task)

        #args = args + dep_args
        #kwargs.update(dep_args)

        args, kwargs = self.filter_params(args, kwargs, task)
        return StaticParameters(args, kwargs)

class ParameterSet:
    """Base class for parameter sets
    
    A parameter set is a container of args and kwargs
    which can be fetched using files, attributes etc.

    Args (in this context) are positional arguments/data that
    are set to a task without giving a name. A tuple

    Kwargs (in this context) are keyword arguments that are 
    set to a task using a name/key. A dictionary
    """
    pass

class StaticParameters(ParameterSet):

    def __init__(self, *static_args, **static_kwargs):
        self.static_args = static_args
        self.static_kwargs = static_kwargs

    @property
    def args(self):
        pass

    @property
    def kwargs(self):
        pass

    def remove_unpicklable(self):
        "Remove args and kwargs that cannot be pickled (in case of multiprocessing)"
        raise NotImplementedError

class PickleParameters(ParameterSet):
    "Get parameters from pickle file"
    def __init__(self, file):
        self.file = file

    @property
    def args(self):
        pass

    @property
    def kwargs(self):
        pass

class YamlParameters(ParameterSet):
    "Get parameters from YAML file"

