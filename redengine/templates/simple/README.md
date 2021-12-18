# Scheduling project: <TARGET>
> This is a template project to
  get started with Red Engine.

## Starting the scheduler

```shell
cd <TARGET>
python main.py
```

Note that this template require additional dependencies
due to the FlaskAPI. You can install them using:

```console
pip install waitress flask flask-restful
```

## Development

Checklist:
- Add your task arguments to `parameters.py`.
- Add your tasks to a `tasks.py` file located in `tasks/`
    - You can structure the tasks by creating subdirectories
      like `tasks/fetch/tasks.py` and `tasks/transform/prices/tasks.py`.
- Add your custom models to `models/`
- Modify `main.py` as needed. This defines the scheduling session.

See documents: https://red-engine.readthedocs.io/en/stable/