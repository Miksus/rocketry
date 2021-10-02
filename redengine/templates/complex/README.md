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
python -m my_package start
```

Or specify the `env`

```shell
python -m my_package start --env prod
```

## Run a specific task

```shell
python -m my_package run my_pytask_1 --env dev
```

## Development

Checklist:
- Add your task arguments to `my_package/arguments.py`.
- Add your tasks to a `tasks.py` or `tasks.yaml` file located in `my_package/tasks/`
- Add your pipelines (extensions) to `extensions.yaml` file located in `my_package/tasks/`
- Add your custom models to `my_package/models/`
- Modify `my_package/config.yaml` as needed. This defines the scheduling session.
- Rename `my_package`:
    - Rename directory `my_package/`
    - Rename directory in `MANIFEST.in`
    - Change the absolute imports in `my_package/**/*.py` files
    - Rename the package in `my_package/setup.py`


See documents: https://red-engine.readthedocs.io/en/latest/