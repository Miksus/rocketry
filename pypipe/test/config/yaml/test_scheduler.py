
import pypipe

def test_from_module_folder(tmpdir):
    conf = tmpdir.join("schedconf.yaml") # .mkdir("sub")
    pytasks = tmpdir.mkdir("python_tasks")

    pytasks.join("fetch_data.py").write("""
def main():
    pass""")

    pytasks.join("transform_data.py").write("""
def main():
    pass""")

    scheduler = pypipe.from_conf(str(conf))
    tasks = scheduler.tasks
    assert 2 == len(tasks)
    assert "fetch_data" == tasks[0].name
    assert "transform_data" == tasks[1].name


def test_from_project_folder(tmpdir):
    conf = tmpdir.join("schedconf.yaml") # .mkdir("sub")

    pytasks = tmpdir.mkdir("python_tasks")

    pytasks.mkdir("fetch_data").join("main.py").write("""
from pypipe.conditions import task_run
START_CONDITION = task_run

def main():
    pass""")

    pytasks.mkdir("transform_data").join("main.py").write("""
from pypipe.conditions import task_run
START_CONDITION = task_run("fetch_data") & (has_ram > 0.5)

def main():
    pass""")

    scheduler = pypipe.from_conf(str(conf))
    tasks = scheduler.tasks
    assert 2 == len(tasks)
    assert "fetch_data" == tasks[0].name
    assert "transform_data" == tasks[1].name

    assert tasks[0].start_cond == task_run("fetch_data")
    assert tasks[1].start_cond == task_run("fetch_data") & (has_ram > 0.5)



def test_advanced(tmpdir):
    conf = tmpdir.join("schedconf.yaml") # .mkdir("sub")
    
    conf.write("""
maintain_tasks: maintain/tasks
shut_condition: scheduler_on.past("5 hours") 
logger: csv
tasks_maintain:
	tasks_py: python_tasks/
	tasks_nb: notebooks/
	tasks_cl: scripts/
....
    """)

    pytasks = tmpdir.mkdir("python_tasks")
    pytasks.join("fetch_data.py").write("""
def main():
    pass""")
    pytasks.join("transform_data.py").write("""
def main():
    pass""")

    nbtasks = tmpdir.mkdir("notebooks")
    nbtasks.join("report.ipynb").write("""
def main():
    pass""")

    cltasks = tmpdir.mkdir("scripts")
    cltasks.join("command.bat").write("""
echo Hello World""")

    scheduler = pypipe.from_conf(str(tmpdir))
    tasks = scheduler.tasks