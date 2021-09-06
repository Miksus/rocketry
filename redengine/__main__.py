import argparse
from pathlib import Path
from typing import Optional

from redengine import Scheduler

from distutils.dir_util import copy_tree

# https://docs.python.org/3/library/argparse.html
PKG_ROOT = Path(__file__).parent

def start_project(target, template):
    template_dir = PKG_ROOT / "templates"
    source = template_dir / template
    if not source.is_dir():
        tmpls = [folder.name for folder in template_dir.glob("*/")]
        raise OSError(f"Template '{template}' does not exists. Full list: {tmpls}")
    copy_tree(str(source), str(target))

def parse_args(args):
    parser = argparse.ArgumentParser(prog='Redengine', description="Scheduling framework.")

    # See: https://docs.python.org/3/library/argparse.html#sub-commands
    subparsers = parser.add_subparsers(help='Command to use.', dest='command')

    start_project_parser = subparsers.add_parser("create", parents=[], add_help=False, aliases=['quick-start'])
    
    start_project_parser.set_defaults(func=start_project)

    start_project_parser.add_argument("target", default="scheduling-project", nargs='?', help='Name of the foder for the project.')
    start_project_parser.add_argument("-t", "-template", default="minimal", dest="template", help='Template to use.', required=False)
    
    return parser.parse_args(args)

def main(args=None):
    #main2()
    args = parse_args(args)

    args = vars(args)
    func = args.pop("func")
    args.pop("command")
    return func(**args)

if __name__ == "__main__":
    main()