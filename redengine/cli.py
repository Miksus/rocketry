
import argparse
import datetime
from pathlib import Path

PKG_ROOT = Path(__file__).parent
TEMPLATE_DIR = PKG_ROOT / "templates"

TEMPLATE_OPTIONS = [folder.name for folder in TEMPLATE_DIR.glob("*/")]

def render(cont:str, variables:dict):
    for repl, val in variables.items():
        cont = cont.replace(repl, val)
    return cont

def start_project(target, template):
    target = Path(target)
    source = TEMPLATE_DIR / template
    if not source.is_dir():
        raise OSError(f"Template '{template}' does not exists. Full list: {TEMPLATE_OPTIONS}")
    if target.is_dir():
        raise OSError(f"Target already exists.")

    variables = {
        "<TARGET>": target.name,
        "<TIMENOW>": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    for file in source.glob("**/*.*"):
        if any(not_this in file.parts for not_this in ("__pycache__",)):
            continue
        new_file = target / file.relative_to(source)
        new_file.parent.mkdir(parents=True, exist_ok=True)
        with open(new_file, "w") as tgt:
            with open(file, "r") as src:
                content = src.read()
                content = render(content, variables=variables)
                tgt.write(content)

def parse_args(args=None):
    parser = argparse.ArgumentParser(prog='Redengine', description="Scheduling framework.")

    subparsers = parser.add_subparsers(help='Command to use.', dest='command')

    start_project_parser = subparsers.add_parser("create", parents=[], add_help=True, aliases=['quick-start'])
    
    start_project_parser.set_defaults(func=start_project)

    start_project_parser.add_argument("target", default="engine-project", nargs='?', help='Name of the foder for the project.')
    start_project_parser.add_argument("-t", "--template", default="minimal", dest="template", help=f'Template to generate. (Options: {TEMPLATE_OPTIONS})', required=False)
    
    return parser.parse_args(args)

def main(args=None):

    args = parse_args(args)

    args = vars(args)
    func = args.pop("func")
    args.pop("command")
    return func(**args)
