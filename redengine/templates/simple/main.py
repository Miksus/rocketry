
from pathlib import Path
from redengine import session
from redengine.tasks.loaders import PyLoader
from redengine.tasks.api import FlaskAPI


# Importing custom
# ----------------

from models import conditions, hooks
import parameters


# Setting the session
# -------------------

session.set_scheme('log_simple') 
# Alternatively use 'log_memory', 'log_csv', 
# or create the logger yourself

session.config.update({
    # Set how tasks are run if execution not specified
    'task_execution': 'process', 

    # Set seconds waited after each cycle of tasks. 
    # Useful to preserve resources. If None, no wait.
    'cycle_sleep': None, 

    # Set whether the logs are read each time a time
    # condition is checked. If false, cached times are
    # used if possible reducing the amount of file reads.
    'force_status_from_logs': False,
})


# Creating meta tasks
# -------------------

# Create a loader (loads Python files from a folder)
root_dir = Path(__file__).parent
PyLoader(path=root_dir / 'tasks/', glob='**/tasks.py')

# Create an API for the session
FlaskAPI(host='127.0.0.1', port=5000)


# Starting up
# -----------

if __name__ == "__main__":
    session.start()