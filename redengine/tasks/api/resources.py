
from redengine._base import RedBase
from redengine.tasks import CodeTask, FuncTask
from redengine import core
from redengine.pybox import query

class RedResource(RedBase):
    """Base class for resources"""
    resources = {}

    def get_kwargs(self, **kwargs):
        return kwargs

    def format_output(self, out):
        return out

def register_resource():
    def wrapper(cls):
        RedResource.resources[cls.__name__] = cls
        return cls
    return wrapper

def call_resource(name:str, method:str, data:dict):
    res = RedResource.resources[name]()
    func = getattr(res, method.lower())
    return func(**data)

@register_resource()
class Task(RedResource):
    """Resource of a single task"""

    def post(self, name, **kwargs):
        """Create a task

        Parameters
        ----------
        name : str
            Name of the task
        kwargs : dict
            Values for the task initiation. If ``class``
            not specified, the class is:
            
            - :py:class:`redengine.tasks.FuncTask` if ``func`` key is specified
            - :py:class:`redengine.tasks.CodeTask` if ``code`` key is specified
        """
        cmd = self.get_kwargs(**kwargs)
        cmd['name'] = name
        if 'class' in cmd:
            core.Task.from_dict(cmd)
            return
        is_func_task = 'func' in cmd
        is_code_task = 'code' in cmd
        if is_func_task:
            FuncTask(**cmd)
        elif is_code_task:
            CodeTask(**cmd)
        else:
            raise ValueError(f"Invalid command: {cmd}")

    def get(self, name):
        """Get a task of given name

        Parameters
        ----------
        name : str
            Name of the task to get
        """
        task = self.session.get_task(name)
        d = task.to_dict()

        # Removing some session specific
        d.pop('session')
        return self.format_output(d)

    def patch(self, name, **kwargs):
        """Patch (partial update) a task attributes
        
        Parameters
        ----------
        name : str
            Name of the task to patch
        **kwargs : dict
            Attributes to update and their updated values.
        """
        kwargs = self.get_kwargs(**kwargs)
        task = self.session.get_task(name)
        with task.lock:
            for attr, val in kwargs.items():
                setattr(task, attr, val)

    def delete(self, name):
        """Delete a task

        Parameters
        ----------
        name : str
            Name of the task to delete
        """
        task = self.session.get_task(name)
        with task.lock:
            task.delete()

@register_resource()
class Tasks(RedResource):
    """Resource of session tasks"""

    def get(self, **kwargs):
        "Get session tasks"
        kwargs = self.get_kwargs(**kwargs)
        qry = query.parser.from_obj(kwargs)
        tasks = []
        for task in self.session.tasks.values():
            task_dict = task.to_dict()
            task_dict.pop('session')
            if qry.match(task_dict):
                tasks.append(task_dict)
        return self.format_output(tasks)

@register_resource()
class Logs(RedResource):
    """Resource of task logs"""

    def get(self, **kwargs):
        """Get task log records"""
        kwargs = self.get_kwargs(**kwargs)

        qry = query.parser.from_obj(kwargs)
        logs = self.session.get_task_log(qry)
        return self.format_output(list(logs))

@register_resource()
class Parameters(RedResource):
    """Resource of session parameters"""

    def get(self):
        "Get session parameters"
        params = self.session.parameters.to_dict()
        return self.format_output(params)

    def patch(self, **kwargs):
        """Patch (partial update) session parameters
        
        Parameters
        ----------
        **kwargs : dict
            Parameters to update and their updated values.
        """
        self.session.parameters.update(self.get_kwargs(**kwargs))

@register_resource()
class Configs(RedResource):
    """Resource of session configs"""

    def get(self):
        "Get session configurations"
        return self.session.config

    def patch(self, **kwargs):
        """Patch (partial update) session configurations

        Parameters
        ----------
        **kwargs : dict
            Configurations to update and their updated values.
        """
        kwargs = self.get_kwargs(**kwargs)
        self.session.config.update(kwargs)

@register_resource()
class Session(RedResource):
    """Resource of the session"""

    def get(self):
        "Get information about the session"
        sess = self.session
        sess_dict = {
            "config": sess.config,
            "parameters": sess.parameters.to_dict(),
            "tasks": list(sess.tasks.keys()),
            "returns": sess.returns.to_dict(),
        }
        return self.format_output(sess_dict)

# Views
@register_resource()
class Dependencies(RedResource):
    """Resource of task dependency information"""

    def get(self, **kwargs):
        "Get information about the session"
        kwargs = self.get_kwargs(**kwargs)

        qry = query.parser.from_obj(kwargs)

        deps = []
        for link in self.session.dependencies:
            d = {
                'parent': link.parent.name,
                'child': link.child.name,
                'relation': link.relation.__name__,
                'type': link.type.__name__ if link.type is not None else None,
            }
            if qry.match(d):
                deps.append(d)
        return deps