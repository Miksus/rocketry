
EXECUTION = "thread"

import datetime

from rocketry.tasks import FuncTask
from rocketry.arguments import Return
from rocketry import session

session.set_scheme("log_memory")

def myfunc():
    ...

def final():
    print(f"Time: {datetime.datetime.now()}")

for i in range(500):
    FuncTask(myfunc, execution=EXECUTION, start_cond="minutely", name=f'task_{i}')

FuncTask(final, execution=EXECUTION, start_cond="minutely", name="final")

if __name__ == "__main__":
    session.start()