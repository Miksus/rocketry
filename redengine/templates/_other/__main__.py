
from pathlib import Path
import sys
from argparse import ArgumentParser
import argparse
from typing import List, Optional

from .main import session

CONFIG_SCHEDULER = Path(__file__).parent / "scheduler/config.yaml"

def exec_task(tasks:List[str], env:str, obey_cond:bool, execution:Optional[str]=None):
    # Find the tasks first
    loader = session.tasks["Loader"]
    loader.execution = 'main'
    loader.execute_action()

    for task_name in tasks:
        task = session.tasks[task_name]
        if obey_cond and not bool(task):
            continue
        if execution is not None:
            task.execution = execution
        task()
    
    # Wait till all tasks are finished
    session.scheduler.wait_task_alive()
    session.scheduler.handle_logs()

def exec_sched():
    main()

def parse_args(args=None):
    parser = argparse.ArgumentParser(prog='Red engine package template', description="Your description here.")

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

    subparsers = parser.add_subparsers(help='Component to use', dest='initiation')

    sched_parser = subparsers.add_parser("start", parents=[env_parser], add_help=True)
    sched_parser.set_defaults(func=exec_sched)

    exec_parser = subparsers.add_parser("run", parents=[env_parser], add_help=True, aliases=['exec']) # 
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
    exec_parser.set_defaults(func=exec_task)

    return parser.parse_args(args)


def main(args=None):
    #main2()
    args = parse_args(args)
    
    args = vars(args)
    func = args.pop("func")
    args.pop("initiation")
    print(args)
    return func(**args)

if __name__ == "__main__":
    main(["start", "--env", "prod"])