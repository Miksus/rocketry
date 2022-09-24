from rocketry.args import Private
from rocketry.tasks import FuncTask
from rocketry.conditions import TaskStarted
from rocketry.args import FuncArg

def run_task(secret, public, secret_list, task_secret, task_public):
    assert public == "hello"
    assert secret == "psst"
    assert secret_list == [1, 2, 3]
    assert task_secret == "hsss"
    assert task_public == "world"

def simple_task_func(value):
    pass

def func_with_return():
    return "x"

def func_with_arg(myparam):
    assert myparam == "x"

def test_parametrization_private(session):

    session.parameters.update({"secret": Private("psst"), "public": "hello", "secret_list": Private([1,2,3])})

    task = FuncTask(
        run_task,
        name="a task",
        execution="main",
        parameters={"task_secret": Private("hsss"), "task_public": "world"},
        session=session
    )
    task.run()
    session.config.shut_cond = TaskStarted(task="a task") >= 1
    session.start()

    assert "success" == task.status

def test_params_failure(session):
    session.config.silence_task_prerun = True

    def get_value():
        raise RuntimeError("Not working")

    task = FuncTask(simple_task_func, parameters={'value': FuncArg(get_value)}, name="a task", execution="main", session=session)
    task.run()

    assert task.status is None

    session.config.shut_cond = TaskStarted(task="a task") >= 1
    session.start()

    assert "fail" == task.status
