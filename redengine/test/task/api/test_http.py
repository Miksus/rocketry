from pathlib import Path

import pytest
from log_helpers import log_task_record

from redengine.arguments.builtin import FuncArg
from redengine.conditions.scheduler import SchedulerCycles
from redengine.parse.condition import parse_condition

from redengine.tasks.api import FlaskAPI
from redengine.tasks import CodeTask
from redengine.tasks.command import CommandTask
from redengine.tasks.func import FuncTask
from redengine.core import Scheduler

from redengine.log import AttributeFormatter
import logging

@pytest.fixture
def api_task(session):
    pytest.importorskip("flask")

    return FlaskAPI(host='127.0.0.1', port=12700, force_run=True)

@pytest.fixture
def client(tmpdir, api_task):
    pytest.importorskip("flask")

    app = api_task.create_app()
    with tmpdir.as_cwd() as old_cwd:
        with app.test_client() as client:
            #with app.app_context():
            #    myapp.init_db()
            yield client

def do_nothing():
    ...

@pytest.mark.parametrize('url,expected',
    [
        pytest.param('/tasks/code-task', {
            'code':"print('hello world')",
            'daemon':None,
            'disabled':False,
            'end_cond':'false',
            'execution':'process',
            'force_run':False,
            'force_termination':False,
            'last_fail':None,
            'last_inaction':None,
            'last_run':'2021-01-01 12:00:00',
            'last_success':'2021-01-01 12:01:00',
            'last_terminate':None,
            'logger':'<TaskAdapter redengine.task (INFO)>',
            'name':'code-task',
            'on_shutdown':False,
            'on_startup':False,
            'output_variable':'return_value',
            'parameters':{},
            'permanent_task':False,
            'priority':0,
            'return_arg':"<class 'redengine.arguments.builtin.Return'>",
            'start_cond':'false',
            'status':'success',
            'timeout':None,
        }, id='/tasks/code-task'),
        pytest.param('/parameters', {
            'myparam1':"a value",
            'myparam2': ['foo', 'bar'],
            'myparam3': {'foo': 1, 'bar': 2},
            'myparam4': 'FuncArg(do_nothing)',
        }, id='/parameters'),
        pytest.param('/configs', {
            'use_instance_naming':False,
            'task_priority':0,
            'task_execution':'process',
            'task_pre_exist':'raise',
            'force_status_from_logs':False,
            'task_logger_basename':'redengine.task',
            'scheduler_logger_basename':'redengine.scheduler',
            'silence_task_prerun':False,
            'silence_cond_check':False,
            'cycle_sleep':None,
            'debug':True,
        }, id='/configs'),
        pytest.param('/session', {
            'config':{
                'use_instance_naming':False,
                'task_priority':0,
                'task_execution':'process',
                'task_pre_exist':'raise',
                'force_status_from_logs':False,
                'task_logger_basename':'redengine.task',
                'scheduler_logger_basename':'redengine.scheduler',
                'silence_task_prerun':False,
                'silence_cond_check':False,
                'cycle_sleep':None,
                'debug':True,
            },
            'parameters':{
                'myparam1': 'a value', 
                'myparam2': ['foo', 'bar'], 
                'myparam3': {'foo': 1, 'bar': 2},
                'myparam4': 'FuncArg(do_nothing)',
            },
            'tasks':['flask-api', 'code-task', 'another-task'],
            'returns':{},
        }, id='/session'),
        pytest.param('/tasks', 
        [
            {
                'daemon':None,
                'disabled':False,
                'end_cond':'false',
                'execution':'thread',
                'force_run':True,
                'force_termination':False,
                'last_fail':None,
                'last_inaction':None,
                'last_run':None,
                'last_success':None,
                'last_terminate':None,
                'logger':'<TaskAdapter redengine.task (INFO)>',
                'name':'flask-api',
                'on_shutdown':False,
                'on_startup':True,
                'parameters':{},
                'permanent_task':True,
                'priority':0,
                'return_arg':"<class 'redengine.arguments.builtin.Return'>",
                'start_cond':'false',
                'status':None,
                'timeout':None,
            },
            {
                'code':"print('hello world')",
                'daemon':None,
                'disabled':False,
                'end_cond':'false',
                'execution':'process',
                'force_run':False,
                'force_termination':False,
                'last_fail':None,
                'last_inaction':None,
                'last_run':'2021-01-01 12:00:00',
                'last_success':'2021-01-01 12:01:00',
                'last_terminate':None,
                'logger':'<TaskAdapter redengine.task (INFO)>',
                'name':'code-task',
                'on_shutdown':False,
                'on_startup':False,
                'output_variable':'return_value',
                'parameters':{},
                'permanent_task':False,
                'priority':0,
                'return_arg':"<class 'redengine.arguments.builtin.Return'>",
                'start_cond':'false',
                'status':'success',
                'timeout':None,
            },
            {
                'code':"print('hello world')",
                'daemon':None,
                'disabled':False,
                'end_cond':'false',
                'execution':'process',
                'force_run':False,
                'force_termination':False,
                'last_fail':'2021-01-01 13:01:00',
                'last_inaction':None,
                'last_run':'2021-01-01 13:00:00',
                'last_success':None,
                'last_terminate':None,
                'logger':'<TaskAdapter redengine.task (INFO)>',
                'name':'another-task',
                'on_shutdown':False,
                'on_startup':False,
                'output_variable':'return_value',
                'parameters':{},
                'permanent_task':False,
                'priority':0,
                'return_arg':"<class 'redengine.arguments.builtin.Return'>",
                'start_cond':'false',
                'status':'fail',
                'timeout':None,
            },
        ], id='/tasks'),

        pytest.param('/logs', 
        [
            {'task_name': 'code-task', 'action': 'run', 'start': '2021-01-01 12:00:00', 'timestamp': '2021-01-01 12:00:00', 'created': 1609495200},
            {'task_name': 'code-task', 'action': 'success', 'start': '2021-01-01 12:00:00', 'timestamp': '2021-01-01 12:01:00', 'end': '2021-01-01 12:01:00', 'runtime': '0 days 00:01:00', 'created': 1609495260},
            {'task_name': 'another-task', 'action': 'run', 'start': '2021-01-01 13:00:00', 'timestamp': '2021-01-01 13:00:00', 'created': 1609498800},
            {'task_name': 'another-task', 'action': 'fail', 'start': '2021-01-01 13:00:00', 'timestamp': '2021-01-01 13:01:00', 'end': '2021-01-01 13:01:00', 'runtime': '0 days 00:01:00', 'created': 1609498860},
        ], id='/logs'),

        pytest.param(
            '/logs?action=run', 
            [
                {'task_name': 'code-task', 'action': 'run', 'start': '2021-01-01 12:00:00', 'timestamp': '2021-01-01 12:00:00', 'created': 1609495200},
                {'task_name': 'another-task', 'action': 'run', 'start': '2021-01-01 13:00:00', 'timestamp': '2021-01-01 13:00:00', 'created': 1609498800},
            ],
            id='/logs?action=run'
        ),

        pytest.param(
            '/logs?timestamp$min=2021-01-01 11:00:00&timestamp$max=2021-01-01 12:00:30', 
            [{'task_name': 'code-task', 'action': 'run', 'start': '2021-01-01 12:00:00', 'timestamp': '2021-01-01 12:00:00', 'created': 1609495200},], 
            id='/logs?timestamp$min=...&timestamp$max=...'
        ),

        pytest.param(
            '/logs?timestamp$min=2021-01-01 13:00:30', 
            [{'task_name': 'another-task', 'action': 'fail', 'start': '2021-01-01 13:00:00', 'timestamp': '2021-01-01 13:01:00', 'end': '2021-01-01 13:01:00', 'runtime': '0 days 00:01:00', 'created': 1609498860}],
            id='/logs?timestamp$min=...'
        ),
        pytest.param(
            '/logs?timestamp$min=2021-01-01 13:01:00', 
            [{'task_name': 'another-task', 'action': 'fail', 'start': '2021-01-01 13:00:00', 'timestamp': '2021-01-01 13:01:00', 'end': '2021-01-01 13:01:00', 'runtime': '0 days 00:01:00', 'created': 1609498860}],
            id='/logs?timestamp$min=<including>'
        ),

        pytest.param(
            '/logs?action=run&action=fail', 
            [
                {'task_name': 'code-task', 'action': 'run', 'start': '2021-01-01 12:00:00', 'timestamp': '2021-01-01 12:00:00', 'created': 1609495200},
                {'task_name': 'another-task', 'action': 'run', 'start': '2021-01-01 13:00:00', 'timestamp': '2021-01-01 13:00:00', 'created': 1609498800},
                {'task_name': 'another-task', 'action': 'fail', 'start': '2021-01-01 13:00:00', 'timestamp': '2021-01-01 13:01:00', 'end': '2021-01-01 13:01:00', 'runtime': '0 days 00:01:00', 'created': 1609498860},
            ],
            id='/logs?action=run&action=fail'
        ),
    ]
)
def test_get(url, expected, client, session):
    # Prune the log records
    logger = logging.getLogger('redengine.task')
    mem_handler = logger.handlers[0]
    mem_handler.formatter = AttributeFormatter(include=['task_name', 'action', 'created', 'start', 'end', 'runtime'])

    # Create couple of example stuff
    task1 = CodeTask("print('hello world')", name="code-task")
    task2 = CodeTask("print('hello world')", name="another-task")
    session.parameters['myparam1'] = 'a value'
    session.parameters['myparam2'] = ['foo', 'bar']
    session.parameters['myparam3'] = {'foo': 1, 'bar': 2}
    session.parameters['myparam4'] = FuncArg(do_nothing)

    log_task_record(task1, '2021-01-01 12:00:00', 'run')
    log_task_record(task1, '2021-01-01 12:01:00', 'success', start_time='2021-01-01 12:00:00')

    log_task_record(task2, '2021-01-01 13:00:00', 'run')
    log_task_record(task2, '2021-01-01 13:01:00', 'fail', start_time='2021-01-01 13:00:00')

    response = client.get(url)
    assert response.status_code == 200

    data = response.get_json()
    assert data == expected

@pytest.mark.parametrize('data,cls,attrs',
    [
        pytest.param({
            'code': 'print("hello world")',
            'start_cond': 'time of day between 12:00 and 14:00',
        }, CodeTask, {
            'code': 'print("hello world")',
            'start_cond': 'time of day between 12:00 and 14:00',
            'force_run': False
        }, id='CodeTask (class unspecified)'),
        pytest.param({
            'path': 'path/to/myfile.py',
            'func': 'main',
            'start_cond': 'time of day between 12:00 and 14:00',
        }, FuncTask, {
            'path': Path('path/to/myfile.py'),
            'func_name': 'main',
            'start_cond': 'time of day between 12:00 and 14:00',
            'force_run': False
        }, id='FuncTask (class unspecified)'),
        pytest.param({
            'class': 'CommandTask',
            'command': 'python -V',
            'start_cond': 'time of day between 12:00 and 14:00',
        }, CommandTask, {
            'command': 'python -V',
            'start_cond': 'time of day between 12:00 and 14:00',
            'force_run': False
        }, id='CommandTask (class specified)'),
    ]
)
def test_task_post(client, session, data, attrs, cls):
    # Create couple of example tasks
    task = CodeTask("print('hello world')", name="code-task")

    response = client.post(
        '/tasks/new-task', 
        json=data
    )
    assert response.status_code == 200

    new_task = session.tasks['new-task']
    assert isinstance(new_task, cls)
    for attr, val in attrs.items():
        if attr in ('start_cond', 'end_cond'):
            val = parse_condition(val)
        assert getattr(new_task, attr) == val

def test_task_patch(client, session):
    # Create couple of example tasks
    task = CodeTask("print('hello world')", name="code-task")

    response = client.patch(
        '/tasks/code-task', 
        json={'start_cond':'time of day between 10:00 and 12:00', 'force_run': True}
    )
    assert response.status_code == 200

    assert task.start_cond == parse_condition('time of day between 10:00 and 12:00')
    assert task.force_run
    assert task.name == 'code-task'

def test_task_delete(client, session):
    # Create couple of example tasks
    task = CodeTask("print('hello world')", name="code-task")
    task_unaffected = CodeTask("print('hello world')", name="code-task-2")

    response = client.delete(
        '/tasks/code-task', 
    )
    assert response.status_code == 200

    assert len(session.tasks) == 2
    assert 'code-task' not in session.tasks
    assert session.tasks['code-task-2'] is task_unaffected

def test_config_patch(client, session):
    # Create couple of example tasks

    response = client.patch(
        '/configs', 
        json={'task_execution': 'thread'}
    )
    assert response.status_code == 200

    assert session.config['task_execution'] == 'thread'
    assert session.config['task_pre_exist'] == 'raise'

def test_params_patch(client, session):
    # Create couple of example tasks
    session.parameters['pre_existing'] = 1
    session.parameters['overridden'] = 'original'
    response = client.patch(
        '/parameters', 
        json={'myparam1': 'a value', 'overridden': 'new'}
    )
    assert response.status_code == 200

    assert session.parameters.to_dict() == {'myparam1': 'a value', 'pre_existing': 1, 'overridden': 'new'}

def test_execute(session, api_task, client):
    sched = Scheduler(shut_cond=SchedulerCycles() >=10)
    sched()
    assert api_task.status == 'success'