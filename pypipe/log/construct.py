

def set_default_logger(logger=None, filename="log/tasks.csv"):
    # Emptying existing handlers
    if logger is None:
        logger = __name__
    elif isinstance(logger, str):
        logger = logging.getLogger(logger)

    logger.handlers = []

    # Making sure the log folder is found
    Path(filename).parent.mkdir(parents=True, exist_ok=True)

    # Adding the default handler
    handler = CsvHandler(
        filename,
        fields=[
            "asctime",
            "levelname",
            "action",
            "task_name",
            "exc_text",
        ]
    )

    logger.addHandler(handler)


def reset_task(filename=None, filename_maintain=None):
    filename = "log/task.csv" if filename is None else filename
    set_default_logger("pypipe.schedule.task", filename=filename)

    filename_maintain = "log/maintain.csv" if filename_maintain is None else filename_maintain
    set_default_logger("pypipe.schedule.task.maintain", filename=filename_maintain)

def reset_schedule(filename=None):
    filename = "log/scheduler.csv" if filename is None else filename
    set_default_logger("pypipe.schedule.scheduler", filename=filename)