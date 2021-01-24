
from atlas import session
from atlas.core.parameters import Parameters

def parse_params(conf:dict, scheduler):
    """Parse the parameters section of a config
    """
    params = Parameters(**conf)
    session.parameters.update(params)