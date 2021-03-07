

def get_dependencies(task):
    """Get tasks the inputted task depends on
    
    Otherwords, get tasks that are required to be successfully
    completed before the inputted task to be executed: 
    the inputted task depends on these tasks."""
    stmt = task.start_condition

    # TODO: Don't put the task itself to dependent tasks
    dep_tasks = []
    if isinstance(stmt, (TaskSucceeded,)):
        dep_task = stmt.session.get_task(stmt.kwargs["task"])
        if dep_task is not task:
            dep_tasks.append(dep_task)

    elif isinstance(stmt, And):
        for sub_stmt in stmt:
            if isinstance(sub_stmt, (TaskSucceeded,)):
                dep_task = sub_stmt.session.get_task(sub_stmt.kwargs["task"])
                if dep_task is not task:
                    dep_tasks.append(sub_stmt.kwargs["task"]) 
    else:
        raise
    return dep_tasks

def get_execution(task):
    """Get the condition that defines the time interval 
    the task is executed with"""
    stmt = task.start_condition

    if isinstance(stmt, (TaskFinished,)):
        if stmt.kwargs["task"] == task:
            return stmt
        else:
            return None
    elif isinstance(stmt, And):
        task_periods = []
        for sub_stmt in stmt:
            if isinstance(sub_stmt, (TaskFinished,)) and sub_stmt.kwargs["task"] == task:
                
                task_periods.append(sub_stmt.period) 
        return TaskFinished(task=task, period=time.All(*task_periods))