from .parse import parse_dict
from pathlib import Path
from pybox.io import read_yaml

def parse_yaml(path):
    conf = read_yaml(path)
    return parse_dict(conf)

def get_default(name):
    # From atlas/config/default
    root = Path(__file__).parent / "defaults"
    path = root / (name + ".yaml")
    return parse_yaml(path)