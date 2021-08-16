
from powerbase.core.parameters import Parameters
from .utils import _get_session

def parse_session_params(conf:dict, **kwargs) -> None:
    """Parse the parameters section of a config
    """
    if not conf:
        return
    params = Parameters(**conf)
    _get_session().parameters.update(params)