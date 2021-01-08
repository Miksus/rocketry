
from pypipe.core.task import base
from pypipe.core.time import StaticInterval, Any, All
from pypipe.conditions import TaskFinished, TaskSucceeded

def get_dependencies(task):
    """Get tasks the inputted task depends on
    
    Otherwords, get tasks that are required to be successfully
    completed before the inputted task to be executed: 
    the inputted task depends on these tasks."""
    task = base.get_task(task)
    stmt = task.start_cond

    # TODO: Don't put the task itself to dependent tasks
    dep_tasks = []
    if isinstance(stmt, (TaskSucceeded,)):
        dep_task = base.get_task(stmt._kwargs["task"])
        if dep_task is not task:
            dep_tasks.append(dep_task)

    elif isinstance(stmt, All):
        for sub_stmt in stmt:
            if isinstance(sub_stmt, (TaskSucceeded,)):
                dep_task = base.get_task(sub_stmt._kwargs["task"])
                if dep_task is not task:
                    dep_tasks.append(sub_stmt._kwargs["task"]) 
    else:
        return None
    return dep_tasks

def get_execution(task):
    """Get the condition that defines the time interval 
    the task is executed with"""
    task = base.get_task(task)
    stmt = task.start_cond

    if isinstance(stmt, (TaskFinished,)):
        if base.get_task(stmt._kwargs["task"]) is task:
            return stmt
        else:
            return StaticInterval()

    elif isinstance(stmt, All):
        task_periods = []
        for sub_stmt in stmt:

            if isinstance(sub_stmt, (TaskFinished,)) and base.get_task(sub_stmt._kwargs["task"]) is task:
                
                task_periods.append(sub_stmt.period) 
        return TaskFinished(task=task, period=All(*task_periods))
    else:
        return StaticInterval()