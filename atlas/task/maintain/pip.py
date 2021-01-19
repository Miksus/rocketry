
from atlas.core.task import Task

class PipInstall(Task):
    def execute_action(self, interpreter=None, file=None, **kwargs):
        if interpreter is None:
            interpreter = sys.executable
        if file is None:
            file = "requirements.txt"
        # https://pip.pypa.io/en/stable/reference/pip_install/#install-requirement
        subprocess.check_call([interpreter, "-m", "pip", "install", "-r", file])