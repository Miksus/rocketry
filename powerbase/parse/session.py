from .utils import DictInstanceParser, StaticParser, Field
from .task import parse_task, parse_tasks
from .misc import parse_logging, parse_clear_existing, parse_strategies, parse_sequences#, parse_tasks
from .parameters import parse_session_params
from .scheduler import parse_scheduler

class SessionParser(StaticParser):

    def __call__(self, *args, session=None, **kwargs):
        from powerbase import Session
        if session is None:
            session = Session()
        super().__call__(*args, session=session, **kwargs)
        return session

parse_session = SessionParser({
        "clear_existing": Field(parse_clear_existing, if_missing="ignore", types=(bool,)),
        "logging": Field(parse_logging, if_missing="ignore"),
        "parameters": Field(parse_session_params, if_missing="ignore", types=(dict,)),
        "tasks": Field(parse_tasks, if_missing="ignore", types=(dict,)),
        # "sequences": Field(parse_sequences, if_missing="ignore"),
        "scheduler": Field(parse_scheduler, if_missing="ignore"),
    },
    on_extra="ignore", 
)

