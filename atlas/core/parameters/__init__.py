from .parameters import Parameters
from .arguments import Argument

GLOBAL_PARAMETERS = Parameters()

def clear_parameters():
    global GLOBAL_PARAMETERS
    GLOBAL_PARAMETERS = {}