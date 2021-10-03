
from pathlib import Path
import os
from redengine import Session

# Importing the custom classes (uncomment needed)
# from models.conditions import MyCondition
# from models.tasks import MyTask
# from models.extensions import MyExtension

root_dir = Path(__file__).parent

session = Session.from_yaml(root_dir / "config.yaml", kwds_fields={"tasks": {"kwds_subparser": {"root": root_dir}}})

# Note that arguments should be imported
# after creating the session.
from . import arguments

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