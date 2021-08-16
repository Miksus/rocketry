import argparse

from powerbase import Scheduler

from powerbase.task import ScriptTask, JupyterTask, CommandTask

# https://docs.python.org/3/library/argparse.html

SCHEDULERS = {
    "simple": Scheduler,
}


def main():
    parser = argparse.ArgumentParser(description='Pypipe Scheduler')

    # Scheduler args
    parser.add_argument('--type', '-t', type=str,
                        help='type of the scheduler to initiate',
                        choices=list(SCHEDULERS.keys()), default="multi")

    parser.add_argument('--min_sleep', type=int,
                        help='minimum wait time in seconds between cycles')

    parser.add_argument('--max_sleep', type=int,
                        help='maximum wait time in seconds between cycles')

    # Task folders
    parser.add_argument('--pytasks', type=str, 
                        help='folder where the python tasks are')

    parser.add_argument('--nbtasks', type=str, 
                        help='folder where the notebook tasks are')

    parser.add_argument('--cltasks', type=str, 
                        help='folder where the command line tasks are')

    parser.add_argument('--config', '-c', type=str, 
                        help='set scheduler config file')

    parser.add_argument('--sum', dest='accumulate', action='store_const',
                        const=sum, default=max,
                        help='sum the integers (default: find the max)')

    args = parser.parse_args()
    
    cls_scheduler = SCHEDULERS[args.type]

    sched_kwargs = dict(
        min_sleep=args.min_sleep,
        max_wait=args.max_sleep,

    )

    # Handle configs
    # ...

    # Get tasks
    # ...
    tasks = []
    if args.pytasks:
        tasks += ScriptTask.from_folder(args.pytasks)
    if args.cltasks:
        tasks += CommandTask.from_folder(args.cltasks)
    if args.nbtasks:
        tasks += JupyterTask.from_folder(args.nbtasks)

    scheduler = cls_scheduler(tasks, **sched_kwargs)
