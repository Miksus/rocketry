
from pathlib import Path

from .base import Statement

# IO related
@Statement()
def flag_file_exists(task, folder, suffix=".flag"):
    "Check whether "
    filename = str(task.name) + suffix

    file = Path(folder) / filename
    if file.is_file():
        # Force the task run next time
        task.force_state = True

        # Remove the flag file
        file.unlink()
        return True
    else:
        return False