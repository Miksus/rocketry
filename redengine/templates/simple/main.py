
from pathlib import Path
from redengine import Session

# Setting up the session
root_dir = Path(__file__).parent
session = Session.from_yaml(
    root_dir / "config.yaml", 
    root=root_dir,
)
session.set_as_default()

# Importing the arguments.
# Note the session must be set as default
# before importing.
import arguments

def main():
    """start scheduling session"""
    session.start()

if __name__ == "__main__":
    main()