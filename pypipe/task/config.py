
import yaml
from pathlib import Path

def parse_config(path):
    folder = path if path.is_dir() else Path(*path.parts[:-1])

    py_conf = folder / "taskconf.py"
    yaml_conf = folder / "taskconf.yaml"

    if yaml_conf.is_file():
        return parse_yaml(yaml_conf)
    elif py_conf.is_file():
        return parse_py(py_conf)
    else:
        return {}

def parse_condition(string):
    return eval(start_cond, {})

def parse_py(path):
    spec = importlib.util.spec_from_file_location("task", path)
    module = importlib.util.module_from_spec(spec)

    
    return dict(
        start_cond=getattr(module, "start_condition", None),
        end_cond=getattr(module, "end_condition", None),
        run_cond=getattr(module, "run_condition", None),
        dependent=getattr(module, "dependent", None),
        execution=getattr(module, "execution", None),
    )

def parse_yaml(path):
    with open(path, 'r') as file:
        cont = yaml.safe_load(file)
    start_cond = cont.get("start_condition", None)
    run_cond = cont.get("run_condition", None)
    end_cond = cont.get("end_condition", None)

    dependent = cont.get("dependent", None)
    execution = cont.get("execution", None)

    start_cond = parse_condition(start_cond)
    run_cond = parse_condition(run_cond)
    end_cond = evparse_conditional(end_cond)

    return dict(
        start_cond=start_cond,
        end_cond=end_cond,
        run_cond=run_cond,
        dependent=dependent,
        execution=execution,
    )