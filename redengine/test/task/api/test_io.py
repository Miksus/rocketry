
import re

from redengine.core.schedule import Scheduler
from redengine.tasks.api import JSONAPI
from redengine.tasks import FuncTask
from redengine.parse import parse_condition
from redengine.conditions import SchedulerCycles
from redengine import Session

from pathlib import Path
from textwrap import dedent

import pytest
from log_helpers import log_task_record


@pytest.mark.parametrize('cmd,expected',
    [
        pytest.param('''
        [
            {"RESOURCE": "Task", "METHOD": "get", "name": "mytask"}
        ]
        ''', '''
            {
                "permanent_task": false,
                "daemon": null,
                "return_arg": "<class 'redengine.arguments.builtin.Return'>",
                "name": "mytask",
                "logger": "<TaskAdapter redengine.task (INFO)>",
                "execution": "main",
                "priority": 0,
                "disabled": false,
                "force_run": false,
                "force_termination": false,
                "status": "success",
                "timeout": null,
                "parameters": {},
                "start_cond": "daily",
                "end_cond": "false",
                "on_startup": false,
                "on_shutdown": false,
                "last_run": "2021-01-01 12:00:00",
                "last_success": "2021-01-01 13:00:00",
                "last_fail": null,
                "last_terminate": null,
                "last_inaction": null,
                "func": "<function test_get.<locals>.<lambda> at <__id__>>"
            }
        ''', id='get_task'),
        pytest.param('''
        [
            {"RESOURCE": "Session", "METHOD": "get"}
        ]
        ''', '''
            {
                "config": {
                    "use_instance_naming": false,
                    "task_priority": 0,
                    "task_execution": "process",
                    "task_pre_exist": "raise",
                    "force_status_from_logs": false,
                    "task_logger_basename": "redengine.task",
                    "scheduler_logger_basename": "redengine.scheduler",
                    "silence_task_prerun": false,
                    "silence_cond_check": false,
                    "cycle_sleep": null,
                    "debug": true
                },
                "parameters": {},
                "tasks": [
                    "api.json",
                    "mytask"
                ],
                "returns": {}
            }
        ''', id='get_session')
    ]
)
def test_get(session, tmpdir, cmd, expected):
    with tmpdir.as_cwd() as old_dir:
        api = JSONAPI(path='commands.json', path_display='output.json')
        mytask = FuncTask(name='mytask', func=lambda: None, execution='main', start_cond='daily')
        log_task_record(mytask, '2021-01-01 12:00:00', 'run')
        log_task_record(mytask, '2021-01-01 13:00:00', 'success', start_time='2021-01-01 12:00:00')

        Path('commands.json').write_text(dedent(cmd))
        api.handle_requests()

        # Comamnd file should be empty
        assert Path('commands.json').read_text() == ''

        output = Path('output.json').read_text()
        output = re.sub(r'(?<=<function test_get\.<locals>\.<lambda> at ).+(?=>)', '<__id__>', output)
        assert dedent(expected).strip() == output

@pytest.mark.parametrize('cmd,attrs',
    [
        pytest.param('''
        [
            {
                "RESOURCE": "Task",
                "METHOD": "post",
                "name": "mytask",
                "start_cond": "time of day between 10:00 and 12:00", 
                "path": "mycode.py",
                "func": "main"
            }
        ]
        ''', 
        #                 "code": "def main():\\n    raise RuntimeError"
        {
            'name': 'mytask',
            'start_cond': 'time of day between 10:00 and 12:00',
            'path': Path('mycode.py'),
            'func_name': 'main',
        }, 
        id='FuncTask'),
        pytest.param('''
        [
            {
                "RESOURCE": "Task",
                "METHOD": "post",
                "name": "mytask",
                "start_cond": "time of day between 10:00 and 12:00", 
                "code": "def main():\\n    raise RuntimeError"
            }
        ]
        ''', {
            'name': 'mytask',
            'start_cond': 'time of day between 10:00 and 12:00',
            'code': 'def main():\n    raise RuntimeError',
        }, 
        id='CodeTask'),
    ]
)
def test_post(session, tmpdir, cmd, attrs):
    with tmpdir.as_cwd() as old_dir:
        tmpdir.join('mycode.py').write('def main():\n    ...')
        api = JSONAPI(path='commands.json', path_display='output.json', path_history='history.jsonl')

        Path('commands.json').write_text(dedent(cmd))
        api.handle_requests()

        # Comamnd file should be empty
        assert Path('commands.json').read_text() == ''

        assert attrs['name'] in session.tasks
        task = session.get_task(attrs['name'])

        for attr, exp_val in attrs.items():
            attr_val = getattr(task, attr)
            if attr == 'start_cond':
                assert attr_val == parse_condition(exp_val)
            else:
                assert attr_val == exp_val
        
        # Test rereading the command
        new_session = Session()
        api = JSONAPI(path='commands.json', path_display='output.json', path_history='history.jsonl')
        api.setup()
        #api.handle_requests()
        assert attrs['name'] in new_session.tasks


@pytest.mark.parametrize('cmd,attrs',
    [
        pytest.param('''
        [
            {
                "RESOURCE": "Task",
                "METHOD": "patch",
                "name": "mytask",
                "start_cond": "time of day between 10:00 and 12:00"
            }
        ]
        ''', {
            'name': 'mytask',
            'start_cond': 'time of day between 10:00 and 12:00',
            'execution': 'main'
        }, 
        id='change start_cond'),
    ]
)
def test_patch(session, tmpdir, cmd, attrs):
    with tmpdir.as_cwd() as old_dir:
        api = JSONAPI(path='commands.json', path_display='output.json', path_history='history.jsonl')
        mytask = FuncTask(name='mytask', func=lambda: None, execution='main', start_cond='daily')

        Path('commands.json').write_text(dedent(cmd))
        api.handle_requests()

        # Comamnd file should be empty
        assert Path('commands.json').read_text() == ''

        assert attrs['name'] in session.tasks
        task = session.get_task(attrs['name'])

        for attr, exp_val in attrs.items():
            attr_val = getattr(task, attr)
            if attr == 'start_cond':
                assert attr_val == parse_condition(exp_val)
            else:
                assert attr_val == exp_val

        # Test rereading the command
        new_session = Session()
        api = JSONAPI(path='commands.json', path_display='output.json', path_history='history.jsonl')
        mytask = FuncTask(name='mytask', func=lambda: None, execution='main', start_cond='daily')
        api.setup()
        task = new_session.get_task(attrs['name'])
        for attr, exp_val in attrs.items():
            attr_val = getattr(task, attr)
            if attr == 'start_cond':
                assert attr_val == parse_condition(exp_val)
            else:
                assert attr_val == exp_val


def test_delete(session, tmpdir):
    with tmpdir.as_cwd() as old_dir:
        api = JSONAPI(path='commands.json', path_display='output.json', path_history='history.jsonl')
        mytask = FuncTask(name='mytask', func=lambda: None, execution='main', start_cond='daily')

        Path('commands.json').write_text(dedent('''
        [
            {
                "RESOURCE": "Task",
                "METHOD": "delete",
                "name": "mytask"
            }
        ]
        '''))
        api.handle_requests()

        # Comamnd file should be empty
        assert Path('commands.json').read_text() == ''

        assert "mytask" not in session.tasks

        # Test rereading the command
        new_session = Session()
        api = JSONAPI(path='commands.json', path_display='output.json', path_history='history.jsonl')
        mytask = FuncTask(name='mytask', func=lambda: None, execution='main', start_cond='daily')
        assert "mytask" in new_session.tasks
        api.setup()
        #api.handle_requests()
        assert "mytask" not in new_session.tasks

def test_run(session, tmpdir):
    def make_command():
        Path('commands.json').write_text(dedent('''
        [
            {
                "RESOURCE": "Task",
                "METHOD": "post",
                "name": "mytask",
                "force_run": true,
                "execution": "main",
                "code": "return_value = 'my return'"
            }
        ]
        '''))
    with tmpdir.as_cwd() as old_dir:
        api = JSONAPI(path='commands.json', path_display='output.json', path_history='history.jsonl', delay=0)
        task_post = FuncTask(name='make_command', func=make_command, execution='main', force_run=True)

        scheduler = Scheduler(shut_cond=SchedulerCycles() >= 3)
        scheduler()
        assert task_post.status == 'success'
        assert 'mytask' in session.tasks
        assert session.returns['mytask'] == 'my return'

        # Test rereading the history
        new_session = Session()
        api = JSONAPI(path='commands.json', path_display='output.json', path_history='history.jsonl', delay=0)
        scheduler = Scheduler(shut_cond=SchedulerCycles() >= 3)

        assert 'mytask' not in new_session.tasks

        scheduler()
        assert 'mytask' in new_session.tasks
        assert session.returns['mytask'] == 'my return'