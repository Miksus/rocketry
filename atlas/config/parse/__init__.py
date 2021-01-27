
# Reading config files
from pybox.io import read_yaml
from pathlib import Path

from .parse import parse_dict

def parse_yaml(path):
    conf = read_yaml(path)
    return parse_dict(conf)

def get_default(name):
    # From atlas/config/default
    root = Path(__file__).parent.parent / "defaults"
    path = root / (name + ".yaml")
    return parse_yaml(path)