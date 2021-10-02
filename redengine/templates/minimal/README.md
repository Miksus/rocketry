# Scheduling project: <TARGET>
> This is a template project to
  get started with Red Engine.

## Starting the scheduler

```shell
cd <TARGET>
python main.py
```

## Development

Checklist:
- Add your task arguments to `arguments.py`.
- Add your tasks to a `tasks.py` file located in `tasks/`
    - You can structure the tasks by creating subdirectories
      like `tasks/fetch/tasks.py` and `tasks/transform/prices/tasks.py`.
- Add your custom models to `models/`
- Modify `config.yaml` as needed. This defines the scheduling session.
    - Change `Loggers: ... handlers: ... redengine.task: ` to 
      different handler in case you want to store the task logging
      records to another storage location, like CSV or Mongo DB.
    - Change the `tasks: ...` if you wish to add some other meta tasks to
      run when the session is started but the tasks are not loaded. For
      example, you can use other loaders than `PyLoader`.
    - You can also add some parameters to `parameters: ...` that
      are shared between tasks.


See documents: https://red-engine.readthedocs.io/en/latest/