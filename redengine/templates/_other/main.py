from pathlib import Path
from redengine.config import parse_yaml

# from models.conditions import MyCondition
# from models.tasks import MyTask
# from models.extensions import MyExtension

ROOT_DIR = Path(__file__).parent

session = parse_yaml(ROOT_DIR / "config.yaml")

def main():
    """Read the scheduling configuration and 
    start scheduling session"""
    session.start()

if __name__ == "__main__":
    main()