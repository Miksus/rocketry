


# Add settings here that you wish to
# import to the tasks. 

# Optionally you can use arguments.py
# to pass arguments for tasks if you
# need to generate the values when 
# the task function is called (instead
# of initiating them once).

import os

if os.environ['ENV'] == "prod":
    # Put production settings here
    my_setting = "Not me"
else:
    # Put testing settings here
    my_setting = "Maybe me"

# Put shared settings here
author = "Me"