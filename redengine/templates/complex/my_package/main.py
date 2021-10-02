from pathlib import Path
from redengine.config import parse_yaml
import os

# Importing the custom classes (uncomment needed)
# from models.conditions import MyCondition
# from models.tasks import MyTask
# from models.extensions import MyExtension

root_dir = Path(__file__).parent

session = parse_yaml(root_dir / "config.yaml", kwds_fields={"tasks": {"kwds_subparser": {"root": root_dir}}})
session.set_as_default()

try:
    from . import arguments
except ImportError:
    import arguments

def set_env(env):
    """Set environment."""
    session.parameters["env"] = env

    # Set to environment variables temporarily
    os.environ["ENV"] = env

def main(env="prod"):
    """Read the scheduling configuration and 
    start scheduling session"""
    set_env(env)
    session.start()

if __name__ == "__main__":
    main()