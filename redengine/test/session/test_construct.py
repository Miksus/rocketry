
import datetime
import os
from textwrap import dedent

import pytest

from redengine import Session
from redengine.parse import parse_condition, parse_time
from redengine.session import Config
from redengine.tasks import FuncTask
from redengine.core import Task, Scheduler, BaseCondition, BaseArgument, Parameters

def assert_default(session:Session):
    for cls in (Task, Scheduler, BaseCondition, BaseArgument, Parameters):
        assert cls.session is session


class TestInit:

    def test_empty(self):
        session = Session()
        session.set_as_default()
        assert session.parameters.to_dict() == {}
        assert session.returns.to_dict() == {}
        assert session.tasks == set()

        config = session.config

        assert isinstance(config, Config)
        assert not config.silence_task_prerun
        assert not config.silence_cond_check
        assert config.task_pre_exist == 'raise'
        assert config.timeout == datetime.timedelta(minutes=30)
        #assert config.task_execution == 'main'

        assert session.env is None
        assert_default(session)

    def test_params(self):
        session = Session(parameters={"x": 1, "y": 2, "env": "prod"})
        assert session.parameters.to_dict() == {"x": 1, "y": 2, "env": "prod"}
        assert session.tasks == {}
        assert session.env == "prod"

    def test_tasks(self):

        session = Session(tasks=[
            FuncTask(path="something.py", func="main", name="my-task-1"),
            FuncTask(path="another.py", func="myfunc", name="my-task-2")
        ])
    
        assert list(session.tasks.keys()) == ["my-task-1", "my-task-2"]
        assert all(isinstance(task, FuncTask) for task in session.tasks.values())
        assert [(str(task.path), task.func_name) for task in session.tasks.values()] == [("something.py", "main"), ("another.py", "myfunc")]

    def test_tasks_lazy(self):

        session = Session()
        FuncTask(path="something.py", func="main", name="my-task-1")
        FuncTask(path="another.py", func="myfunc", name="my-task-2")

        assert list(session.tasks.keys()) == ["my-task-1", "my-task-2"]
        assert all(isinstance(task, FuncTask) for task in session.tasks.values())
        assert [(str(task.path), task.func_name) for task in session.tasks.values()] == [("something.py", "main"), ("another.py", "myfunc")]

    def test_scheduler(self):
        session = Session(kwds_scheduler={
            "name": "my_scheduler",
            "restarting": "relaunch",
            "instant_shutdown": True,
            "shut_cond": "scheduler has run over 5 hours",
            "max_processes": 5,
        })
        scheduler = session.scheduler
        assert scheduler.name == "my_scheduler"
        assert scheduler.restarting == "relaunch"
        assert scheduler.instant_shutdown == True
        assert scheduler.max_processes == 5

        assert scheduler.shut_cond == parse_condition("scheduler has run over 5 hours")

    def test_sequence(self):
        session = Session(tasks=[
            FuncTask(path="something.py", func="main", name="my-task-1"),
            FuncTask(path="another.py", func="myfunc", name="my-task-2")
        ], extensions=[
            Sequence(tasks=["my-task-1", "my-task-2"], interval="every 2 hours", name="my-sequence-1"),
            Sequence(tasks=["my-task-2", "my-task-1"], name="my-sequence-2"),
        ])
        seqs = session.extensions["sequences"]
        assert list(seqs.keys()) == ["my-sequence-1", "my-sequence-2"]

        assert [task.name for task in seqs["my-sequence-1"].tasks] == ["my-task-1", "my-task-2"]
        assert [task.name for task in seqs["my-sequence-2"].tasks] == ["my-task-2", "my-task-1"]

        assert seqs["my-sequence-1"].interval == parse_time("every 2 hours")
        assert seqs["my-sequence-2"].interval is None

    def test_set_cls_condition(self):
        session = Session()
        class MyCond(BaseCondition):
            __parsers__ = {"is my foo": "__init__"}
            def __bool__(self):
                return True
        
        assert "is my foo" in session.cond_parsers
        # Create new, should reset
        session = Session()
        assert "is my foo" not in session.cond_parsers
        assert len(session.cond_parsers) > 0


class TestDict:

    def test_empty(self):
        session = Session.from_dict({})
        assert session.parameters.to_dict() == {}
        assert session.tasks == {}
        assert_default(session)

    def test_params(self):
        session = Session.from_dict({"parameters": {"x": 1, "y": 2}})
        assert session.parameters.to_dict() == {"x": 1, "y": 2}
        assert session.tasks == {}

    def test_tasks_dict(self):
        conf = {
            "tasks": {
                "my-task-1": {"class": "FuncTask", "path": "something.py", "func": "main"},
                "my-task-2": {"class": "FuncTask", "path": "another.py", "func": "myfunc"},
            }
        }
        session = Session.from_dict(conf)
        assert list(session.tasks.keys()) == ["my-task-1", "my-task-2"]
        assert all(isinstance(task, FuncTask) for task in session.tasks.values())
        assert [(str(task.path), task.func_name) for task in session.tasks.values()] == [("something.py", "main"), ("another.py", "myfunc")]

    def test_tasks_list(self):
        conf = {
            "tasks": [
                {"class": "FuncTask", "path": "something.py", "func": "main", "name": "my-task-1"},
                {"class": "FuncTask", "path": "another.py", "func": "myfunc", "name": "my-task-2"},
            ]
        }
        session = Session.from_dict(conf)
        assert list(session.tasks.keys()) == ["my-task-1", "my-task-2"]
        assert all(isinstance(task, FuncTask) for task in session.tasks.values())
        assert [(str(task.path), task.func_name) for task in session.tasks.values()] == [("something.py", "main"), ("another.py", "myfunc")]

    def test_scheduler(self):
        conf = {
            "scheduler": {
                "name": "my_scheduler",
                "restarting": "relaunch",
                "instant_shutdown": True,
                "shut_cond": "scheduler has run over 5 hours",
                "max_processes": 5,
            }
        }
        session = Session.from_dict(conf)
        scheduler = session.scheduler
        assert scheduler.name == "my_scheduler"
        assert scheduler.restarting == "relaunch"
        assert scheduler.instant_shutdown == True
        assert scheduler.max_processes == 5

        assert scheduler.shut_cond == parse_condition("scheduler has run over 5 hours")

    def test_sequence(self):
        conf = {
            "tasks": [
                {"class": "FuncTask", "path": "something.py", "func": "main", "name": "my-task-1"},
                {"class": "FuncTask", "path": "another.py", "func": "myfunc", "name": "my-task-2"},
            ],
            "sequences": {
                "my-sequence-1": {"tasks": ["my-task-1", "my-task-2"], "interval": "every 2 hours"},
                "my-sequence-2": {"tasks": ["my-task-2", "my-task-1"]},
            }
        }
        session = Session.from_dict(conf)
        seqs = session.extensions["sequences"]
        assert list(seqs.keys()) == ["my-sequence-1", "my-sequence-2"]

        assert [task.name for task in seqs["my-sequence-1"].tasks] == ["my-task-1", "my-task-2"]
        assert [task.name for task in seqs["my-sequence-2"].tasks] == ["my-task-2", "my-task-1"]

        assert seqs["my-sequence-1"].interval == parse_time("every 2 hours")
        assert seqs["my-sequence-2"].interval is None

class TestYAML:

    @pytest.fixture
    def conf_file(self, tmpdir):
        pytest.importorskip("yaml")
        return os.path.join(str(tmpdir), "conf.yaml")

    def write_content(self, c, file):
        with open(file, "w") as f:
            f.write(dedent(c))
        

    def test_empty(self, conf_file):
        content = """
        """
        self.write_content(content, conf_file)
        session = Session.from_yaml(conf_file)

        assert session.parameters.to_dict() == {}
        assert session.tasks == {}
        assert_default(session)

    def test_params(self, conf_file):
        content = """
        parameters:
            x: 1
            y: 2
        """
        self.write_content(content, conf_file)
        session = Session.from_yaml(conf_file)
        assert session.parameters.to_dict() == {"x": 1, "y": 2}
        assert session.tasks == {}

    def test_tasks_dict(self, conf_file):
        content = """
        tasks:
            my-task-1:
                class: FuncTask
                path: something.py
                func: main
            my-task-2:
                class: FuncTask
                path: another.py
                func: myfunc
        """
        self.write_content(content, conf_file)
        session = Session.from_yaml(conf_file)
        assert list(session.tasks.keys()) == ["my-task-1", "my-task-2"]
        assert all(isinstance(task, FuncTask) for task in session.tasks.values())
        assert [(str(task.path), task.func_name) for task in session.tasks.values()] == [("something.py", "main"), ("another.py", "myfunc")]

    def test_tasks_list(self, conf_file):
        content = """
        tasks:
          - name: my-task-1
            class: FuncTask
            path: something.py
            func: main
          - name: my-task-2
            class: FuncTask
            path: another.py
            func: myfunc
        """
        self.write_content(content, conf_file)
        session = Session.from_yaml(conf_file)
        assert list(session.tasks.keys()) == ["my-task-1", "my-task-2"]
        assert all(isinstance(task, FuncTask) for task in session.tasks.values())
        assert [(str(task.path), task.func_name) for task in session.tasks.values()] == [("something.py", "main"), ("another.py", "myfunc")]

    def test_scheduler(self, conf_file):
        content = """
        scheduler:
          name: my_scheduler
          restarting: relaunch
          instant_shutdown: True
          shut_cond: 'scheduler has run over 5 hours'
          max_processes: 5
        """
        self.write_content(content, conf_file)
        session = Session.from_yaml(conf_file)
        scheduler = session.scheduler
        assert scheduler.name == "my_scheduler"
        assert scheduler.restarting == "relaunch"
        assert scheduler.instant_shutdown == True
        assert scheduler.max_processes == 5

        assert scheduler.shut_cond == parse_condition("scheduler has run over 5 hours")

    def test_sequence(self, conf_file):
        content = """
        tasks:
            my-task-1:
                class: FuncTask
                path: something.py
                func: main
            my-task-2:
                class: FuncTask
                path: another.py
                func: myfunc
        sequences:
            my-sequence-1:
                tasks: ['my-task-1', 'my-task-2']
                interval: 'every 2 hours'
            my-sequence-2:
                tasks:
                    - my-task-2
                    - my-task-1
        """
        self.write_content(content, conf_file)
        session = Session.from_yaml(conf_file)
        seqs = session.extensions["sequences"]
        assert list(seqs.keys()) == ["my-sequence-1", "my-sequence-2"]

        assert [task.name for task in seqs["my-sequence-1"].tasks] == ["my-task-1", "my-task-2"]
        assert [task.name for task in seqs["my-sequence-2"].tasks] == ["my-task-2", "my-task-1"]

        assert seqs["my-sequence-1"].interval == parse_time("every 2 hours")
        assert seqs["my-sequence-2"].interval is None