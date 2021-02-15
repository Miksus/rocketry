from .utils import DictInstanceParser, StaticParser, Field
from .task import parse_task
from .misc import parse_logging, parse_clear_existing, parse_strategies, parse_sequences, parse_tasks
from .parameters import parse_session_params
from .scheduler import parse_scheduler


parse_session = StaticParser(
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