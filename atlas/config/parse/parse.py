# Parsing
from .params import parse_session_params
from .scheduler import parse_scheduler
from .sequences import parse_sequences
from .strategies import parse_strategies
from .tasks import parse_tasks
from logging.config import dictConfig

from atlas.core.task import clear_tasks
from atlas.core.schedule import clear_schedulers
from atlas.core.parameters import clear_parameters
from .parser import StaticParser, Field

"""syntax
clear_existing: True|False

parameters:
    mode: test

tasks:
    my-task-1:
        class: FuncTask
        func: maintainers.print_run_log
        ...
    my-task-2
        class: ScriptTask
        path: path/to/script.py
        ...
    my-task-3
        class: PipInstall
        ....

sequences:
    run-seq-1:
        start_cond: daily
        tasks:
            - my-task-1
            - my-task-2



scheduler:
    type: 'multi'|'single'

    tasks:
    - run-seq-1
    - my-task-3
    strategies:
    - personal

"""

def parse_clear_existing(clear, **kwargs):
    if clear:
        clear_tasks()
        clear_schedulers()
        clear_parameters()

def parse_logging(conf, **kwargs):
    dictConfig(conf)


PARSER = StaticParser(
    Field("clear_existing", parse_clear_existing, if_missing="ignore", types=(bool,)),
    Field("logging",        parse_logging,        if_missing="ignore"),
    Field("parameters",     parse_session_params, if_missing="ignore", types=(dict,)),
    Field("tasks",          parse_tasks,          if_missing="ignore", types=(dict,)),
    Field("sequences",      parse_sequences,      if_missing="ignore"),
    Field("strategies",     parse_strategies,     if_missing="ignore"),
    Field("scheduler",      parse_scheduler,      if_missing="ignore"),
    on_extra="ignore", 
    #resources={"strategies": []}
    # Ps: I know this spacing is against PEP8, but do I care? No.
)


def parse_dict(conf):
    return PARSER.parse(conf)