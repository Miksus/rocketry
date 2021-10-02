# Scheduling project: <TARGET>
> This is a template project to
  get started with Red Engine.

## Installing

```shell
cd <TARGET>
python -m pip install -e .
```

Note that we use flag `-e` to make the 
package editable: you don't need to reinstall
it after doing changes in the source code.

## Starting the scheduler

```shell
python -m gearbox start
```

Or specify the `env`

```shell
python -m gearbox start --env prod
```

## Run a specific task

```shell
python -m modern run my_pytask_1 --env dev
```

## Development

Checklist:
- Add your task arguments to `arguments.py`.
- Add your tasks to a `tasks.py` or `tasks.yaml` file located in `tasks/`
    - You can structure the tasks by creating subdirectories
        like `tasks/fetch/tasks.py` and `tasks/transform/prices/tasks.py`,
        or `tasks/fetch/tasks.yaml` and `tasks/transform/prices/tasks.yaml`.
- Add your pipelines (extensions) to `extensions.yaml` file located in `tasks/`
    - Or add them to the `tasks.yaml`
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