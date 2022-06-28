
from . import StaticParser, Field
from . import parse_scheduler, parse_tasks, parse_session_params

session_parser = StaticParser({
        "parameters": Field(parse_session_params, if_missing="ignore", types=(dict,)),
        "tasks": Field(parse_tasks, if_missing="ignore", types=(dict, list)),
        "scheduler": Field(parse_scheduler, if_missing="ignore"),
        # Note that extensions are set in redengine.ext
    },
    on_extra="ignore", 
)