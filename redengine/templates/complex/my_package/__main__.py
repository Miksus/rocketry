
from pathlib import Path
import sys, os
from argparse import ArgumentParser
import argparse
from typing import List, Optional

from .main import session, main as run_main
from . import hooks


def exec_task(tasks:List[str], env:str, obey_cond:bool, execution:Optional[str]=None):
    """Run given task(s)."""
    #for loader_name in ("TaskLoader", "PyLoader"):
    #    loader = session.tasks[loader_name]
    #    loader.execution = 'main'
    #    loader.execute()
    session.scheduler.startup()

    missing_tasks = [task for task in tasks if task not in session.tasks]
    if missing_tasks:
        found_tasks = list(session.tasks.keys())
        raise KeyError(f"Session missing tasks: {missing_tasks} (found: {found_tasks})")

    for task_name in tasks:
        task = session.tasks[task_name]
        if obey_cond and not bool(task):
            continue
        if execution is not None:
            task.execution = execution
        task()
    
    # Wait till all tasks are finished
    # session.scheduler.wait_task_alive()
    # session.scheduler.handle_logs()
    session.scheduler.shut_down()

def exec_sched(env):
    """Start the scheduler"""
    run_main(env)

    for name, task in session.tasks.items():
        print("")
        print(f"{name}")
        print("--------------------")
        print(f"Status: {bool(task)}")
        print(f"Disabled: {task.disabled}")
        print(f"Force run: {task.force_run}")
        print(f"Last run: {task.last_run}")

def set_env(env):
    """Set environment."""
    session.parameters["env"] = env

    # Set to environment variables temporarily
    os.environ["ENV"] = env

def parse_args(args=None):
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(prog='My scheduler.', description="Your description here.")

    env_parser = argparse.ArgumentParser()
    env_parser.add_argument(
        '--env',
        help="Run mode (default 'prod')",
        dest="env",
        choices=['dev', 'test', 'prod'], # Only these can be passed as values
        required=False,
        type=str,
        default="prod"
    )

    subparsers = parser.add_subparsers(dest='initiation')

    sched_parser = subparsers.add_parser("start", parents=[env_parser], add_help=False, help="Start the scheduling session.")
    sched_parser.set_defaults(func=exec_sched)

    exec_parser = subparsers.add_parser("run", parents=[env_parser], add_help=False, aliases=['exec'], help="Run specified task(s).")
    exec_parser.set_defaults(func=exec_task)
    exec_parser.add_argument(
        'tasks',
        nargs="+",
        help='Names of the tasks to execute'
    )
    exec_parser.add_argument(
        '-e', '--execution',
        dest='execution',
        choices=['main', 'thread', 'process'],
        help='Execution type',
        required=False
    )
    exec_parser.add_argument(
        '--obey_cond',
        dest='obey_cond',
        help='Obey the start condition of the task',
        action='store_true',
        required=False
    )
    return parser.parse_args(args)


def main(args=None):
    args = parse_args(args)
    
    args = vars(args)
    func = args.pop("func")
    args.pop("initiation")
    set_env(args["env"])
    return func(**args)

if __name__ == "__main__":
    main()