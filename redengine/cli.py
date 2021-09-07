import argparse
from pathlib import Path
from typing import Optional

from redengine import Scheduler

from distutils.dir_util import copy_tree

PKG_ROOT = Path(__file__).parent
TEMPLATE_DIR = PKG_ROOT / "templates"

TEMPLATE_OPTIONS = [folder.name for folder in TEMPLATE_DIR.glob("*/")]

def start_project(target, template):
    source = TEMPLATE_DIR / template
    if not source.is_dir():
        raise OSError(f"Template '{template}' does not exists. Full list: {TEMPLATE_OPTIONS}")
    copy_tree(str(source), str(target))

def parse_args(args=None):
    parser = argparse.ArgumentParser(prog='Redengine', description="Scheduling framework.")

    subparsers = parser.add_subparsers(help='Command to use.', dest='command')

    start_project_parser = subparsers.add_parser("create", parents=[], add_help=True, aliases=['quick-start'])
    
    start_project_parser.set_defaults(func=start_project)

    start_project_parser.add_argument("target", default="engine-project", nargs='?', help='Name of the foder for the project.')
    start_project_parser.add_argument("-t", "-template", default="minimal", dest="template", help=f'Template to generate. (Options: {TEMPLATE_OPTIONS})', required=False)
    
    return parser.parse_args(args)

def main(args=None):

    args = parse_args(args)

    args = vars(args)
    func = args.pop("func")
    args.pop("command")
    return func(**args)