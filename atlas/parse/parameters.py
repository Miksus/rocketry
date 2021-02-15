
from atlas.core.parameters import Parameters, GLOBAL_PARAMETERS

def parse_session_params(conf:dict, **kwargs) -> None:
    """Parse the parameters section of a config
    """
    if not conf:
        return
    params = Parameters(**conf)
    GLOBAL_PARAMETERS.update(params)