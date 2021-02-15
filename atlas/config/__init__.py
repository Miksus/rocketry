from atlas.parse import parse_session
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

def parse_dict(conf:dict):
    return parse_session(conf)