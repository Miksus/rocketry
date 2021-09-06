from pathlib import Path
from redengine.config import parse_yaml

ROOT_DIR = Path(__file__).parent

def main():
    """Read the scheduling configuration and 
    start scheduling session"""
    session = parse_yaml(ROOT_DIR / "config.yaml")
    session.start()

if __name__ == "__main__":
    main()