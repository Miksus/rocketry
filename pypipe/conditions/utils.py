

def set_defaults(condition, task=None, scheduler=None):
    "Set tasks/scheduler to the condition cluster where those are used and not yet specified like in case where task is given by the task where the condition belongs to"

    if task is not None:
        is_missing = hasattr(condition, "task") and condition.task is None
        if is_missing:
            condition.task = task
        
    if scheduler is not None:
        is_missing = hasattr(condition, "scheduler") and condition.task is None
        if is_missing:
            condition.scheduler = scheduler
        
    sub_conditions = (
        condition.conditions if hasattr(condition, "conditions") 
        else [condition.condition] if hasattr(condition, "condition")
        else []
    )

    for sub_cond in sub_conditions:
        set_defaults(sub_cond, task=task, scheduler=scheduler)