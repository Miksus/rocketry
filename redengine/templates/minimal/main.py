from pathlib import Path
from redengine.config import parse_yaml

# from models.conditions import MyCondition
# from models.tasks import MyTask
# from models.extensions import MyExtension

root_dir = Path(__file__).parent

session = parse_yaml(root_dir / "config.yaml", kwds_fields={"tasks": {"kwds_subparser": {"root":root_dir}}})

def main():
    """start scheduling session"""
    session.start()

if __name__ == "__main__":
    main()